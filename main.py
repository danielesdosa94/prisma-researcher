"""
PRISMA - Automated Research Desktop App
=======================================
Main entry point for the PRISMA application.
A privacy-first research tool for web scraping and AI analysis.

Usage:
    python main.py

Author: PRISMA Team
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import flet as ft

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.theme import COLORS, TYPOGRAPHY, SPACING, CONFIG
from src.ui.layout import MainLayout
from src.utils.logger import PrismaLogger, logger
from src.utils.file_manager import FileManager
from src.utils.url_parser import extract_urls_from_text, parse_url_file
from src.core.scraper import create_scraper, ScrapeResult
from src.core.downloader import ModelDownloader
from src.core.analyzer import create_analyzer


class PrismaApp:
    """
    Main application controller.
    Coordinates UI, scraping, and AI analysis.
    """
    
    def __init__(self, page: ft.Page):
        """
        Initialize the application.
        
        Args:
            page: Flet page instance
        """
        self.page = page
        self.setup_page()
        
        # Initialize components
        self.file_manager = FileManager()
        self.downloader = ModelDownloader()
        self.scraper = create_scraper()
        self.analyzer = create_analyzer()
        
        # State
        self.current_urls: List[str] = []
        self.scraped_results: List[ScrapeResult] = []
        self.is_processing = False
        
        # Build UI
        self.layout = MainLayout(
            on_execute=self.handle_execute,
            on_mode_change=self.handle_mode_change,
            on_file_drop=self.handle_file_drop,
        )
        
        # Set up logger callback
        PrismaLogger.set_ui_callback(self.log_to_terminal)
        
        # Add layout to page
        self.page.add(self.layout)
        
        # Initial status
        self.check_ai_status()
        self.log_to_terminal("PRISMA iniciado. Esperando input...", "info")
    
    def setup_page(self) -> None:
        """Configure the Flet page settings."""
        self.page.title = f"{CONFIG.APP_NAME} - {CONFIG.APP_SUBTITLE}"
        self.page.window.width = CONFIG.WINDOW_WIDTH
        self.page.window.height = CONFIG.WINDOW_HEIGHT
        self.page.window.min_width = CONFIG.WINDOW_MIN_WIDTH
        self.page.window.min_height = CONFIG.WINDOW_MIN_HEIGHT
        self.page.bgcolor = COLORS.BACKGROUND
        self.page.padding = 0
        self.page.spacing = 0
        
        # Theme
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(
            color_scheme_seed=COLORS.PRIMARY,
            font_family=TYPOGRAPHY.FONT_UI,
        )
    
    def log_to_terminal(self, message: str, status: str = "info") -> None:
        """Send log message to UI terminal."""
        if hasattr(self, 'layout') and self.layout:
            self.layout.log(message, status)
            self.page.update()
    
    def check_ai_status(self) -> None:
        """Check and update AI model status."""
        status = self.downloader.get_model_status()
        
        if status["available"]:
            self.layout.control_panel.set_ai_status(
                f"IA lista ({status['size_gb']} GB)",
                available=True
            )
        else:
            self.layout.control_panel.set_ai_status(
                f"IA no descargada (~{status['required_size_gb']} GB)",
                available=False
            )
    
    def handle_file_drop(self, file_paths: List[str]) -> None:
        """
        Handle file drop event.
        
        Args:
            file_paths: List of dropped file paths
        """
        self.log_to_terminal(f"Archivos recibidos: {len(file_paths)}", "info")
        
        asyncio.create_task(self._process_files(file_paths))
    
    async def _process_files(self, file_paths: List[str]) -> None:
        """Process dropped files and extract URLs."""
        all_urls = []
        
        for path_str in file_paths:
            path = Path(path_str)
            self.log_to_terminal(f"Leyendo: {path.name}", "info")
            
            try:
                content = await self.file_manager.read_file(path)
                urls, invalid = parse_url_file(content)
                all_urls.extend(urls)
                
                if invalid:
                    for inv in invalid[:3]:  # Show first 3 invalid
                        self.log_to_terminal(f"Omitido: {inv}", "warning")
                        
            except Exception as e:
                self.log_to_terminal(f"Error leyendo {path.name}: {e}", "error")
        
        # Update URL list
        self.current_urls = list(set(all_urls))  # Deduplicate
        self.layout.update_url_counter(len(self.current_urls))
        
        if self.current_urls:
            self.log_to_terminal(
                f"✓ {len(self.current_urls)} URLs válidas detectadas",
                "success"
            )
    
    def handle_mode_change(self, mode: str) -> None:
        """Handle operation mode change."""
        if mode == "analyze":
            # Check if AI is available
            if not self.downloader.is_model_available():
                self.log_to_terminal(
                    "El modelo de IA no está descargado. Se descargará al ejecutar.",
                    "warning"
                )
    
    def handle_execute(self) -> None:
        """Handle execute button click."""
        if self.is_processing:
            return
        
        # Get URLs from input
        manual_urls = self.layout.get_urls()
        if manual_urls:
            self.current_urls.extend(manual_urls)
            self.current_urls = list(set(self.current_urls))
        
        if not self.current_urls:
            self.log_to_terminal("No hay URLs para procesar", "warning")
            return
        
        # Start processing
        asyncio.create_task(self._execute_pipeline())
    
    async def _execute_pipeline(self) -> None:
        """Execute the full scraping and analysis pipeline."""
        self.is_processing = True
        self.layout.set_executing(True)
        self.layout.terminal_section.hide_report_button()
        
        mode = self.layout.get_mode()
        use_ai = mode == "analyze"
        
        try:
            # Phase 1: Scraping
            self.log_to_terminal("═" * 40, "info")
            self.log_to_terminal("FASE 1: SCRAPING", "info")
            self.log_to_terminal("═" * 40, "info")
            
            # Set up progress callback
            def scrape_progress(current: int, total: int, url: str):
                domain = url.split('/')[2] if '/' in url else url
                self.log_to_terminal(f"[{current}/{total}] Scrapeando: {domain[:40]}...", "info")
            
            self.scraper.set_progress_callback(scrape_progress)
            
            # Execute scraping
            self.scraped_results = await self.scraper.scrape_urls(self.current_urls)
            
            # Save scraped content
            successful = [r for r in self.scraped_results if r.success]
            
            for result in successful:
                filename = f"scrape_{result.title[:30].replace(' ', '_')}.md"
                filename = "".join(c for c in filename if c.isalnum() or c in ('_', '.', '-'))
                await self.file_manager.save_markdown(result.markdown, filename)
            
            self.log_to_terminal(
                f"✓ {len(successful)}/{len(self.scraped_results)} páginas scrapeadas",
                "success"
            )
            
            # Phase 2: AI Analysis (if enabled)
            if use_ai and successful:
                self.log_to_terminal("═" * 40, "ai")
                self.log_to_terminal("FASE 2: ANÁLISIS IA", "ai")
                self.log_to_terminal("═" * 40, "ai")
                
                # Check/download model
                if not self.downloader.is_model_available():
                    self.log_to_terminal("Descargando modelo de IA...", "ai")
                    
                    def download_progress(progress: float, msg: str):
                        self.layout.control_panel.show_progress(progress, msg)
                        self.page.update()
                    
                    self.downloader.set_progress_callback(download_progress)
                    success = await self.downloader.download_model()
                    self.layout.control_panel.hide_progress()
                    
                    if not success:
                        self.log_to_terminal("Error descargando modelo", "error")
                        return
                    
                    self.check_ai_status()
                
                # Load model
                def analyzer_progress(msg: str):
                    self.log_to_terminal(msg, "ai")
                
                self.analyzer.set_progress_callback(analyzer_progress)
                
                if not self.analyzer.is_loaded:
                    loaded = await self.analyzer.load_model(self.downloader.model_path)
                    if not loaded:
                        self.log_to_terminal("Error cargando modelo", "error")
                        return
                
                # Generate report
                contents = [r.markdown for r in successful]
                result = await self.analyzer.generate_research_report(
                    contents,
                    topic="Investigación Web"
                )
                
                if result.success:
                    report_path = await self.file_manager.save_report(result.summary)
                    self.log_to_terminal(f"✓ Reporte generado: {report_path.name}", "success")
                    
                    # Show view report button
                    self.layout.terminal_section.show_report_button(
                        lambda _: self.file_manager.open_file(report_path)
                    )
                else:
                    self.log_to_terminal(f"Error en análisis: {result.error}", "error")
            
            # Completion
            self.log_to_terminal("═" * 40, "success")
            self.log_to_terminal("✓ PROCESO COMPLETADO", "success")
            self.log_to_terminal("═" * 40, "success")
            
            # Open output folder
            self.file_manager.open_output_folder()
            
        except Exception as e:
            self.log_to_terminal(f"Error: {e}", "error")
            logger.exception(f"Pipeline error: {e}")
            
        finally:
            self.is_processing = False
            self.layout.set_executing(False)
            self.layout.set_status("Proceso completado", "success")


def main(page: ft.Page) -> None:
    """
    Main entry point for Flet application.
    
    Args:
        page: Flet page instance
    """
    app = PrismaApp(page)


if __name__ == "__main__":
    # Run the application
    ft.app(target=main)
