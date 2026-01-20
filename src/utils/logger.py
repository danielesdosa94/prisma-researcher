"""
PRISMA - Logger Utility
=======================
Custom logger with colored console output and file logging.
Uses the 'rich' library for beautiful terminal output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
from functools import wraps

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Custom theme matching PRISMA colors
PRISMA_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green",
    "ai": "magenta bold",
    "debug": "dim",
})

# Global console instance
console = Console(theme=PRISMA_THEME)


class PrismaLogger:
    """
    Custom logger for PRISMA application.
    Provides both console and file logging with pretty formatting.
    
    Usage:
        logger = PrismaLogger("ModuleName")
        logger.info("Processing started")
        logger.success("Completed!")
        logger.ai("AI analysis running...")
    """
    
    _instances: dict = {}
    _log_file: Optional[Path] = None
    _ui_callback: Optional[Callable] = None
    
    def __new__(cls, name: str = "PRISMA"):
        """Singleton per name to avoid duplicate handlers."""
        if name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[name] = instance
        return cls._instances[name]
    
    def __init__(self, name: str = "PRISMA"):
        if hasattr(self, '_initialized'):
            return
        
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with Rich
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(console_handler)
        
        self._initialized = True
    
    @classmethod
    def set_log_file(cls, log_dir: Path) -> None:
        """
        Enable file logging to specified directory.
        
        Args:
            log_dir: Directory to store log files
        """
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cls._log_file = log_dir / f"prisma_{timestamp}.log"
        
        # Add file handler to all instances
        file_handler = logging.FileHandler(cls._log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            )
        )
        
        for instance in cls._instances.values():
            instance.logger.addHandler(file_handler)
    
    @classmethod
    def set_ui_callback(cls, callback: Callable[[str, str], None]) -> None:
        """
        Set callback function to send logs to UI.
        
        Args:
            callback: Function that accepts (message, status) parameters
        """
        cls._ui_callback = callback
    
    def _log_to_ui(self, message: str, status: str) -> None:
        """Send log to UI if callback is set."""
        if self._ui_callback:
            try:
                self._ui_callback(message, status)
            except Exception:
                pass  # Don't break logging if UI callback fails
    
    def debug(self, message: str) -> None:
        """Log debug message (console only, not UI)."""
        self.logger.debug(f"[dim]{message}[/dim]")
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(f"[info]{message}[/info]")
        self._log_to_ui(message, "info")
    
    def success(self, message: str) -> None:
        """Log success message."""
        self.logger.info(f"[success]✓ {message}[/success]")
        self._log_to_ui(f"✓ {message}", "success")
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(f"[warning]⚠ {message}[/warning]")
        self._log_to_ui(f"⚠ {message}", "warning")
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(f"[error]✗ {message}[/error]")
        self._log_to_ui(f"✗ {message}", "error")
    
    def ai(self, message: str) -> None:
        """Log AI-related message."""
        self.logger.info(f"[ai]🤖 {message}[/ai]")
        self._log_to_ui(f"🤖 {message}", "ai")
    
    def exception(self, message: str) -> None:
        """Log exception with traceback."""
        self.logger.exception(f"[error]{message}[/error]")
        self._log_to_ui(f"✗ {message}", "error")


def log_execution(logger: Optional[PrismaLogger] = None):
    """
    Decorator to log function execution time and errors.
    
    Usage:
        @log_execution()
        async def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            log = logger or PrismaLogger(func.__module__)
            log.debug(f"Starting {func.__name__}")
            start = datetime.now()
            try:
                result = await func(*args, **kwargs)
                elapsed = (datetime.now() - start).total_seconds()
                log.debug(f"Completed {func.__name__} in {elapsed:.2f}s")
                return result
            except Exception as e:
                log.exception(f"Error in {func.__name__}: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            log = logger or PrismaLogger(func.__module__)
            log.debug(f"Starting {func.__name__}")
            start = datetime.now()
            try:
                result = func(*args, **kwargs)
                elapsed = (datetime.now() - start).total_seconds()
                log.debug(f"Completed {func.__name__} in {elapsed:.2f}s")
                return result
            except Exception as e:
                log.exception(f"Error in {func.__name__}: {e}")
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Create default logger instance
logger = PrismaLogger("PRISMA")
