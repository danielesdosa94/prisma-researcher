"""
PRISMA - Core Package
=====================
Business logic: scraping, AI analysis, model downloading.
"""

from src.core.scraper import WebScraper, ScrapeResult, create_scraper
from src.core.analyzer import AIAnalyzer, AnalysisResult, create_analyzer
from src.core.downloader import ModelDownloader, ensure_model_available

__all__ = [
    "WebScraper",
    "ScrapeResult",
    "create_scraper",
    "AIAnalyzer",
    "AnalysisResult",
    "create_analyzer",
    "ModelDownloader",
    "ensure_model_available",
]
