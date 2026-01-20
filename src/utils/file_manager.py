"""
PRISMA - File Manager
=====================
Handles file operations: reading inputs, saving outputs,
managing the output directory structure.
"""

import os
import re
import asyncio
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

import aiofiles
from docx import Document

from src.utils.logger import PrismaLogger

logger = PrismaLogger("FileManager")


class FileManager:
    """
    Manages file operations for PRISMA.
    Handles reading input files (.txt, .docx) and saving output files.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize FileManager.
        
        Args:
            output_dir: Directory for output files. Defaults to ./output
        """
        self.output_dir = output_dir or Path("output")
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory: {self.output_dir.absolute()}")
    
    def _generate_filename(self, prefix: str, extension: str) -> Path:
        """
        Generate a unique filename with timestamp.
        
        Args:
            prefix: File prefix (e.g., "scrape", "report")
            extension: File extension without dot (e.g., "md", "pdf")
        
        Returns:
            Full path to the new file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{extension}"
        return self.output_dir / filename
    
    async def read_text_file(self, file_path: Path) -> str:
        """
        Read content from a text file asynchronously.
        
        Args:
            file_path: Path to the .txt file
        
        Returns:
            File contents as string
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            logger.debug(f"Read {len(content)} chars from {file_path.name}")
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                content = await f.read()
            logger.warning(f"Used fallback encoding for {file_path.name}")
            return content
    
    def read_docx_file(self, file_path: Path) -> str:
        """
        Read content from a .docx file.
        
        Args:
            file_path: Path to the .docx file
        
        Returns:
            Extracted text content
        """
        try:
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            content = "\n".join(paragraphs)
            logger.debug(f"Extracted {len(paragraphs)} paragraphs from {file_path.name}")
            return content
        except Exception as e:
            logger.error(f"Failed to read DOCX: {e}")
            raise
    
    async def read_file(self, file_path: Path) -> str:
        """
        Read file content based on extension.
        
        Args:
            file_path: Path to the file
        
        Returns:
            File content as string
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return await self.read_text_file(file_path)
        elif extension == '.docx':
            # docx reading is sync, run in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.read_docx_file, file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    async def save_markdown(
        self,
        content: str,
        filename: Optional[str] = None,
        prefix: str = "scrape"
    ) -> Path:
        """
        Save content as a Markdown file.
        
        Args:
            content: Markdown content to save
            filename: Optional custom filename
            prefix: Prefix for auto-generated filename
        
        Returns:
            Path to the saved file
        """
        if filename:
            file_path = self.output_dir / filename
        else:
            file_path = self._generate_filename(prefix, "md")
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        logger.success(f"Saved: {file_path.name}")
        return file_path
    
    async def save_report(
        self,
        content: str,
        title: str = "Research Report",
    ) -> Path:
        """
        Save the final research report.
        
        Args:
            content: Report content in Markdown
            title: Report title (used in header)
        
        Returns:
            Path to the saved report
        """
        # Add header to report
        header = f"""# {title}

**Generado por PRISMA** | {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

"""
        full_content = header + content
        
        return await self.save_markdown(full_content, prefix="report")
    
    def get_output_files(self, extension: Optional[str] = None) -> List[Path]:
        """
        Get list of files in output directory.
        
        Args:
            extension: Filter by extension (without dot)
        
        Returns:
            List of file paths
        """
        if extension:
            pattern = f"*.{extension}"
            return list(self.output_dir.glob(pattern))
        return list(self.output_dir.iterdir())
    
    def open_output_folder(self) -> None:
        """Open the output folder in the system file explorer."""
        import subprocess
        import platform
        
        path = str(self.output_dir.absolute())
        system = platform.system()
        
        try:
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
            logger.info("Opened output folder")
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
    
    def open_file(self, file_path: Path) -> None:
        """Open a file with the default system application."""
        import subprocess
        import platform
        
        path = str(file_path.absolute())
        system = platform.system()
        
        try:
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
            logger.info(f"Opened: {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to open file: {e}")
    
    def cleanup_old_files(self, days: int = 7) -> int:
        """
        Remove files older than specified days.
        
        Args:
            days: Age threshold in days
        
        Returns:
            Number of files removed
        """
        from datetime import timedelta
        
        threshold = datetime.now() - timedelta(days=days)
        removed = 0
        
        for file_path in self.output_dir.iterdir():
            if file_path.is_file() and file_path.name != ".keep":
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < threshold:
                    file_path.unlink()
                    removed += 1
                    logger.debug(f"Removed old file: {file_path.name}")
        
        if removed:
            logger.info(f"Cleaned up {removed} old files")
        
        return removed


# Global instance for convenience
file_manager = FileManager()
