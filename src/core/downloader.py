"""
PRISMA - Model Downloader
=========================
Handles lazy downloading of the AI model from HuggingFace.
Implements progress tracking and verification.
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass

from huggingface_hub import hf_hub_download, snapshot_download
from huggingface_hub.utils import HfHubHTTPError

from src.utils.logger import PrismaLogger
from src.ui.theme import CONFIG

logger = PrismaLogger("Downloader")


@dataclass
class ModelInfo:
    """Information about the AI model."""
    
    name: str = "Qwen 2.5 3B Instruct"
    repo_id: str = "Qwen/Qwen2.5-3B-Instruct-GGUF"
    filename: str = "qwen2.5-3b-instruct-q4_k_m.gguf"
    size_gb: float = 1.8
    quantization: str = "Q4_K_M"
    
    @property
    def size_bytes(self) -> int:
        return int(self.size_gb * 1024 * 1024 * 1024)


class ModelDownloader:
    """
    Handles downloading and verifying AI models.
    Implements lazy loading pattern - only downloads when needed.
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize the downloader.
        
        Args:
            models_dir: Directory to store models. Defaults to assets/models
        """
        self.models_dir = models_dir or Path("assets/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_info = ModelInfo()
        self._progress_callback: Optional[Callable[[float, str], None]] = None
        self._cancel_requested = False
    
    @property
    def model_path(self) -> Path:
        """Get full path to the model file."""
        return self.models_dir / self.model_info.filename
    
    def is_model_available(self) -> bool:
        """
        Check if the model is already downloaded.
        
        Returns:
            True if model exists and has reasonable size
        """
        if not self.model_path.exists():
            return False
        
        # Check file size (should be at least 1GB for this model)
        file_size = self.model_path.stat().st_size
        min_size = 1 * 1024 * 1024 * 1024  # 1GB minimum
        
        if file_size < min_size:
            logger.warning("Model file appears corrupted (too small)")
            return False
        
        return True
    
    def get_model_status(self) -> dict:
        """
        Get current model status information.
        
        Returns:
            Dictionary with model status details
        """
        if self.is_model_available():
            file_size = self.model_path.stat().st_size
            return {
                "available": True,
                "path": str(self.model_path),
                "size_gb": round(file_size / (1024**3), 2),
                "name": self.model_info.name,
            }
        else:
            return {
                "available": False,
                "required_size_gb": self.model_info.size_gb,
                "name": self.model_info.name,
            }
    
    def set_progress_callback(
        self,
        callback: Callable[[float, str], None]
    ) -> None:
        """
        Set callback for download progress updates.
        
        Args:
            callback: Function(progress: 0.0-1.0, message: str)
        """
        self._progress_callback = callback
    
    def cancel_download(self) -> None:
        """Request cancellation of ongoing download."""
        self._cancel_requested = True
        logger.warning("Download cancellation requested")
    
    async def download_model(self) -> bool:
        """
        Download the AI model from HuggingFace.
        
        Returns:
            True if download successful, False otherwise
        """
        if self.is_model_available():
            logger.info("Model already available")
            return True
        
        self._cancel_requested = False
        logger.info(f"Starting download: {self.model_info.name}")
        logger.info(f"Size: ~{self.model_info.size_gb} GB")
        
        if self._progress_callback:
            self._progress_callback(0.0, "Conectando a HuggingFace...")
        
        try:
            # Run download in thread pool to not block async loop
            loop = asyncio.get_event_loop()
            
            def download_sync():
                """Synchronous download function."""
                return hf_hub_download(
                    repo_id=self.model_info.repo_id,
                    filename=self.model_info.filename,
                    local_dir=self.models_dir,
                    local_dir_use_symlinks=False,
                    resume_download=True,
                )
            
            # Start download
            if self._progress_callback:
                self._progress_callback(0.05, "Descargando modelo...")
            
            # Execute download
            downloaded_path = await loop.run_in_executor(None, download_sync)
            
            # Verify download
            if self._cancel_requested:
                logger.warning("Download was cancelled")
                # Clean up partial file
                if self.model_path.exists():
                    self.model_path.unlink()
                return False
            
            if self.is_model_available():
                if self._progress_callback:
                    self._progress_callback(1.0, "¡Descarga completada!")
                logger.success(f"Model downloaded: {downloaded_path}")
                return True
            else:
                raise Exception("Downloaded file verification failed")
            
        except HfHubHTTPError as e:
            error_msg = f"HuggingFace error: {e}"
            logger.error(error_msg)
            if self._progress_callback:
                self._progress_callback(0.0, f"Error: {error_msg[:50]}")
            return False
            
        except Exception as e:
            error_msg = f"Download failed: {e}"
            logger.error(error_msg)
            if self._progress_callback:
                self._progress_callback(0.0, f"Error: {str(e)[:50]}")
            return False
    
    def delete_model(self) -> bool:
        """
        Delete the downloaded model file.
        
        Returns:
            True if deletion successful
        """
        try:
            if self.model_path.exists():
                self.model_path.unlink()
                logger.info("Model deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete model: {e}")
            return False


class ProgressTracker:
    """
    Utility class to track download progress.
    Can be used with tqdm or custom progress bars.
    """
    
    def __init__(
        self,
        total_size: int,
        callback: Optional[Callable[[float, str], None]] = None
    ):
        self.total_size = total_size
        self.downloaded = 0
        self.callback = callback
        self.last_percent = 0
    
    def update(self, chunk_size: int) -> None:
        """Update progress with new chunk."""
        self.downloaded += chunk_size
        percent = int((self.downloaded / self.total_size) * 100)
        
        # Only update on percentage change
        if percent != self.last_percent:
            self.last_percent = percent
            if self.callback:
                progress = self.downloaded / self.total_size
                downloaded_mb = self.downloaded / (1024 * 1024)
                total_mb = self.total_size / (1024 * 1024)
                message = f"Descargando: {downloaded_mb:.1f} / {total_mb:.1f} MB"
                self.callback(progress, message)


# Global instance for convenience
model_downloader = ModelDownloader()


async def ensure_model_available(
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> bool:
    """
    Convenience function to ensure model is available.
    Downloads if necessary.
    
    Args:
        progress_callback: Optional progress callback function
    
    Returns:
        True if model is available
    """
    downloader = ModelDownloader()
    
    if downloader.is_model_available():
        return True
    
    if progress_callback:
        downloader.set_progress_callback(progress_callback)
    
    return await downloader.download_model()
