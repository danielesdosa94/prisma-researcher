"""
PRISMA - Source Package
=======================
Main source code package for PRISMA application.
"""

__version__ = "1.0.0"
__author__ = "PRISMA Team"


"""PRISMA - UI Module"""

from src.ui.theme import COLORS, TYPOGRAPHY, SPACING, CONFIG
from src.ui.app_layout import build_app_ui, UIState

__all__ = [
    "COLORS",
    "TYPOGRAPHY", 
    "SPACING",
    "CONFIG",
    "build_app_ui",
    "UIState",
]

"""PRISMA - Core Module (Business Logic)"""

# Core components are imported lazily to avoid heavy dependencies at startup
__all__ = [
    "WebScraper",
    "create_scraper",
    "AIAnalyzer", 
    "create_analyzer",
    "ModelDownloader",
]

"""PRISMA - Utilities Module"""

from src.utils.logger import PrismaLogger

__all__ = ["PrismaLogger"]