"""
PRISMA - Automated Research Desktop App
========================================
Entry point for the application.

ARCHITECTURE FIX:
- FilePicker is created and added to page.overlay FIRST
- FilePicker is then passed to UI builder via dependency injection
- FilePicker is NEVER part of the visual tree

Author: PRISMA Team
Version: 2.0.0
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import flet as ft

# UI imports
from src.ui.theme import COLORS, CONFIG
from src.ui.app_layout import (
    build_app_ui,
    UIState,
    update_url_counter,
    set_button_state,
    set_status,
    show_progress,
)

# Core imports (with graceful fallback if not available)
try:
    from src.core.scraper import WebScraper, create_scraper, ScrapeResult
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    print("[WARNING] Scraper module not available")

try:
    from src.core.analyzer import AIAnalyzer, create_analyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    print("[WARNING] Analyzer module not available")

try:
    from src.core.downloader import ModelDownloader, ensure_model_available
    DOWNLOADER_AVAILABLE = True
except ImportError:
    DOWNLOADER_AVAILABLE = False
    print("[WARNING] Downloader module not available")


# =============================================================================
# GLOBAL APPLICATION STATE
# =============================================================================

class AppController:
    """
    Application controller that manages UI state and business logic.
    Separates concerns between UI and core functionality.
    """
    
    def __init__(self):
        self.ui_state: Optional[UIState] = None
        self.page: Optional[ft.Page] = None
        self.file_picker: Optional[ft.FilePicker] = None
        
        # Processing state
        self.current_urls: List[str] = []
        self.is_processing: bool = False
        self.scraped_results: List[dict] = []
        
        # Core components (lazy initialized)
        self._scraper: Optional[WebScraper] = None
        self._analyzer: Optional[AIAnalyzer] = None
        self._downloader: Optional[ModelDownloader] = None
    
    @property
    def scraper(self) -> Optional[WebScraper]:
        """Lazy-load scraper instance."""
        if self._scraper is None and SCRAPER_AVAILABLE:
            self._scraper = create_scraper(headless=True)
        return self._scraper
    
    @property
    def analyzer(self) -> Optional[AIAnalyzer]:
        """Lazy-load analyzer instance."""
        if self._analyzer is None and ANALYZER_AVAILABLE:
            self._analyzer = create_analyzer()
        return self._analyzer
    
    @property
    def downloader(self) -> Optional[ModelDownloader]:
        """Lazy-load downloader instance."""
        if self._downloader is None and DOWNLOADER_AVAILABLE:
            self._downloader = ModelDownloader()
        return self._downloader


# Global controller instance
APP = AppController()


# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

def log_to_terminal(message: str, status: str = "info") -> None:
    """
    Add a log entry to the terminal display.
    
    Args:
        message: Log message text
        status: Log type ("info", "success", "error", "warning", "ai")
    """
    if APP.ui_state is None or APP.ui_state.log_column is None:
        print(f"[{status.upper()}] {message}")
        return
    
    color_map = {
        "info": COLORS.TEXT_SECONDARY,
        "success": COLORS.SUCCESS,
        "error": COLORS.ERROR,
        "warning": COLORS.WARNING,
        "ai": COLORS.PRIMARY,
    }
    
    color = color_map.get(status, COLORS.TEXT_SECONDARY)
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    log_entry = ft.Row(
        controls=[
            ft.Text(
                f"[{timestamp}]",
                color=COLORS.TEXT_MUTED,
                size=11,
                font_family="Consolas",
            ),
            ft.Text(
                f"> {message}",
                color=color,
                size=13,
                font_family="Consolas",
                selectable=True,
            ),
        ],
        spacing=8,
    )
    
    APP.ui_state.log_column.controls.append(log_entry)
    
    # Limit log entries to prevent memory issues
    if len(APP.ui_state.log_column.controls) > 200:
        APP.ui_state.log_column.controls.pop(0)
    
    try:
        APP.ui_state.log_column.update()
    except Exception:
        pass


def clear_terminal() -> None:
    """Clear all log entries from terminal."""
    if APP.ui_state and APP.ui_state.log_column:
        APP.ui_state.log_column.controls.clear()
        try:
            APP.ui_state.log_column.update()
        except Exception:
            pass


# =============================================================================
# URL AND FILE PROCESSING
# =============================================================================

def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract valid URLs from text content.
    
    Args:
        text: Text that may contain URLs
    
    Returns:
        List of unique, valid URLs
    """
    # Pattern matches http/https URLs and www. prefixed domains
    url_pattern = r'https?://[^\s<>"\')\]]+|www\.[^\s<>"\')\]]+'
    
    urls = re.findall(url_pattern, text)
    
    # Normalize URLs (add https:// to www. URLs)
    normalized = []
    for url in urls:
        if url.startswith("www."):
            url = f"https://{url}"
        # Clean trailing punctuation that might have been captured
        url = url.rstrip(".,;:!?")
        normalized.append(url)
    
    # Return unique URLs, preserving order
    seen = set()
    unique = []
    for url in normalized:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    
    return unique


async def read_file_content(file_path: str) -> str:
    """
    Read content from a file asynchronously.
    
    Args:
        file_path: Path to file
    
    Returns:
        File content as string
    """
    path = Path(file_path)
    
    try:
        if path.suffix.lower() == '.txt':
            return path.read_text(encoding='utf-8')
        
        elif path.suffix.lower() == '.docx':
            # Try to use python-docx if available
            try:
                from docx import Document
                doc = Document(str(path))
                return '\n'.join(para.text for para in doc.paragraphs)
            except ImportError:
                log_to_terminal("python-docx no instalado, leyendo como texto", "warning")
                return path.read_text(encoding='utf-8', errors='ignore')
        
        else:
            log_to_terminal(f"Formato no soportado: {path.suffix}", "warning")
            return ""
    
    except Exception as e:
        log_to_terminal(f"Error leyendo {path.name}: {e}", "error")
        return ""


async def process_dropped_files(file_paths: List[str]) -> None:
    """
    Process dropped/selected files and extract URLs.
    
    Args:
        file_paths: List of file paths to process
    """
    all_urls = []
    
    for path_str in file_paths:
        path = Path(path_str)
        log_to_terminal(f"Leyendo: {path.name}", "info")
        
        try:
            content = await read_file_content(path_str)
            urls = extract_urls_from_text(content)
            all_urls.extend(urls)
            
            if urls:
                log_to_terminal(f"  → {len(urls)} URLs encontradas", "success")
            else:
                log_to_terminal(f"  → Sin URLs válidas", "warning")
        
        except Exception as e:
            log_to_terminal(f"Error procesando {path.name}: {e}", "error")
    
    # Update global state with unique URLs
    APP.current_urls = list(set(all_urls))
    
    # Update UI counter
    if APP.ui_state:
        update_url_counter(APP.ui_state, len(APP.current_urls))
    
    if APP.current_urls:
        log_to_terminal(
            f"✓ {len(APP.current_urls)} URLs válidas en total",
            "success"
        )


# =============================================================================
# MAIN PIPELINE EXECUTION
# =============================================================================

async def execute_scraping_phase() -> List[dict]:
    """
    Execute the web scraping phase.
    
    Returns:
        List of scrape results as dictionaries
    """
    results = []
    total = len(APP.current_urls)
    
    log_to_terminal("═" * 45, "info")
    log_to_terminal("FASE 1: SCRAPING WEB", "info")
    log_to_terminal("═" * 45, "info")
    
    if APP.scraper:
        # Use real scraper if available
        def progress_callback(current: int, total: int, url: str):
            domain = url.split('/')[2] if '/' in url else url[:30]
            log_to_terminal(f"[{current}/{total}] {domain}", "info")
            
            if APP.ui_state:
                progress = current / total * 0.5  # First 50% for scraping
                show_progress(APP.ui_state, True, progress)
        
        APP.scraper.set_progress_callback(progress_callback)
        
        try:
            scrape_results = await APP.scraper.scrape_urls(APP.current_urls)
            
            for result in scrape_results:
                if result.success:
                    log_to_terminal(f"  ✓ {result.title[:40]}...", "success")
                    results.append({
                        "url": result.url,
                        "title": result.title,
                        "content": result.markdown,
                        "success": True,
                    })
                else:
                    log_to_terminal(f"  ✗ Error: {result.error[:50]}", "error")
                    results.append({
                        "url": result.url,
                        "success": False,
                        "error": result.error,
                    })
        
        except Exception as e:
            log_to_terminal(f"Error en scraper: {e}", "error")
    
    else:
        # Mock scraping for UI testing when scraper not available
        for i, url in enumerate(APP.current_urls, 1):
            domain = url.split('/')[2] if '/' in url else url[:30]
            log_to_terminal(f"[{i}/{total}] Scrapeando: {domain}...", "info")
            
            # Simulate work
            await asyncio.sleep(0.3)
            
            log_to_terminal(f"  ✓ Completado (mock)", "success")
            results.append({
                "url": url,
                "title": f"Mock Title for {domain}",
                "content": f"# Mock Content\n\nContent from {url}",
                "success": True,
            })
            
            if APP.ui_state:
                progress = i / total * 0.5
                show_progress(APP.ui_state, True, progress)
    
    successful = sum(1 for r in results if r.get("success"))
    log_to_terminal(f"✓ {successful}/{total} páginas scrapeadas", "success")
    
    return results


async def execute_analysis_phase(scraped_contents: List[str]) -> Optional[str]:
    """
    Execute the AI analysis phase.
    
    Args:
        scraped_contents: List of scraped markdown contents
    
    Returns:
        Generated report content or None if failed
    """
    log_to_terminal("═" * 45, "ai")
    log_to_terminal("FASE 2: ANÁLISIS CON IA", "ai")
    log_to_terminal("═" * 45, "ai")
    
    if APP.analyzer:
        # Check if model is available
        if APP.downloader and not APP.downloader.is_model_available():
            log_to_terminal("Modelo no encontrado. Descargando...", "ai")
            
            def download_progress(progress: float, message: str):
                log_to_terminal(message, "ai")
                if APP.ui_state:
                    # Map download progress to 50-70% of total
                    total_progress = 0.5 + (progress * 0.2)
                    show_progress(APP.ui_state, True, total_progress)
            
            APP.downloader.set_progress_callback(download_progress)
            success = await APP.downloader.download_model()
            
            if not success:
                log_to_terminal("Error descargando modelo", "error")
                return None
        
        # Load model
        log_to_terminal("Cargando modelo en memoria...", "ai")
        if not await APP.analyzer.load_model():
            log_to_terminal("Error cargando modelo", "error")
            return None
        
        # Generate report
        log_to_terminal("Generando análisis...", "ai")
        
        if APP.ui_state:
            show_progress(APP.ui_state, True, 0.8)
        
        result = await APP.analyzer.generate_research_report(
            scraped_contents,
            topic="Investigación PRISMA"
        )
        
        if result.success:
            log_to_terminal("✓ Análisis completado", "success")
            return result.summary
        else:
            log_to_terminal(f"Error en análisis: {result.error}", "error")
            return None
    
    else:
        # Mock analysis for UI testing
        log_to_terminal("Cargando modelo...", "ai")
        await asyncio.sleep(0.8)
        
        if APP.ui_state:
            show_progress(APP.ui_state, True, 0.6)
        
        log_to_terminal("Analizando contenido...", "ai")
        await asyncio.sleep(1.0)
        
        if APP.ui_state:
            show_progress(APP.ui_state, True, 0.8)
        
        log_to_terminal("Generando informe...", "ai")
        await asyncio.sleep(0.8)
        
        mock_report = f"""# Informe de Investigación PRISMA

## Resumen Ejecutivo

Este informe analiza {len(scraped_contents)} fuentes web recopiladas automáticamente.

## Puntos Clave

1. Se procesaron exitosamente todas las URLs proporcionadas
2. El contenido fue extraído y convertido a formato Markdown
3. Este es un reporte de demostración (módulo de IA no disponible)

## Conclusiones

El sistema PRISMA funcionó correctamente en modo de prueba.

---
*Generado por PRISMA v{CONFIG.APP_VERSION}*
"""
        
        log_to_terminal("✓ Análisis completado (mock)", "success")
        return mock_report


async def save_report(content: str, filename: str = None) -> Path:
    """
    Save the generated report to disk.
    
    Args:
        content: Report content in Markdown
        filename: Optional custom filename
    
    Returns:
        Path to saved file
    """
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prisma_report_{timestamp}.md"
    
    file_path = output_dir / filename
    file_path.write_text(content, encoding='utf-8')
    
    return file_path


async def execute_pipeline() -> None:
    """
    Execute the complete scraping and analysis pipeline.
    """
    if APP.is_processing:
        log_to_terminal("Ya hay un proceso en ejecución", "warning")
        return
    
    # Collect URLs from text input
    if APP.ui_state and APP.ui_state.url_input and APP.ui_state.url_input.value:
        manual_urls = extract_urls_from_text(APP.ui_state.url_input.value)
        APP.current_urls.extend(manual_urls)
        APP.current_urls = list(set(APP.current_urls))
        update_url_counter(APP.ui_state, len(APP.current_urls))
    
    if not APP.current_urls:
        log_to_terminal("No hay URLs para procesar", "warning")
        return
    
    # Mark as processing
    APP.is_processing = True
    
    # Update UI state
    if APP.ui_state:
        set_button_state(APP.ui_state.execute_btn, disabled=True, text="PROCESANDO...")
        set_status(APP.ui_state, "Procesando...", "processing")
        show_progress(APP.ui_state, True, 0)
    
    try:
        # Phase 1: Scraping
        results = await execute_scraping_phase()
        APP.scraped_results = results
        
        # Collect successful content
        scraped_contents = [
            r["content"] for r in results
            if r.get("success") and r.get("content")
        ]
        
        # Save individual scraped files
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        for i, result in enumerate(results):
            if result.get("success"):
                safe_title = re.sub(r'[^\w\s-]', '', result.get("title", f"page_{i}")[:30])
                filename = f"scraped_{i+1}_{safe_title}.md"
                (output_dir / filename).write_text(result.get("content", ""), encoding='utf-8')
        
        # Phase 2: AI Analysis (if enabled)
        use_ai = APP.ui_state and APP.ui_state.ai_switch and APP.ui_state.ai_switch.value
        
        if use_ai and scraped_contents:
            report = await execute_analysis_phase(scraped_contents)
            
            if report:
                report_path = await save_report(report)
                log_to_terminal(f"✓ Reporte guardado: {report_path.name}", "success")
                
                # Show report button
                if APP.ui_state and APP.ui_state.report_btn:
                    APP.ui_state.report_btn.visible = True
                    APP.ui_state.report_btn.data["report_path"] = str(report_path)
                    
                    def open_report(e):
                        import subprocess
                        import sys
                        path = e.control.data.get("report_path")
                        if path:
                            if sys.platform == "win32":
                                subprocess.run(["start", "", path], shell=True)
                            elif sys.platform == "darwin":
                                subprocess.run(["open", path])
                            else:
                                subprocess.run(["xdg-open", path])
                    
                    APP.ui_state.report_btn.on_click = open_report
                    
                    try:
                        APP.ui_state.report_btn.update()
                    except Exception:
                        pass
        
        # Completion
        log_to_terminal("═" * 45, "success")
        log_to_terminal("✓ PROCESO COMPLETADO", "success")
        log_to_terminal(f"  Archivos guardados en: ./output/", "info")
        log_to_terminal("═" * 45, "success")
        
        if APP.ui_state:
            show_progress(APP.ui_state, True, 1.0)
            set_status(APP.ui_state, "Completado", "success")
    
    except Exception as e:
        log_to_terminal(f"Error fatal: {e}", "error")
        if APP.ui_state:
            set_status(APP.ui_state, "Error", "error")
    
    finally:
        # Reset processing state
        APP.is_processing = False
        
        if APP.ui_state:
            set_button_state(
                APP.ui_state.execute_btn,
                disabled=False,
                text="EJECUTAR INVESTIGACIÓN"
            )
            
            # Hide progress after delay
            await asyncio.sleep(2)
            show_progress(APP.ui_state, False)


def handle_execute_click() -> None:
    """Handle execute button click - bridge to async."""
    asyncio.create_task(execute_pipeline())


# =============================================================================
# FILE PICKER EVENT HANDLER
# =============================================================================

def handle_file_picker_result(e: ft.ControlEvent) -> None:
    """
    Handle file picker result event.
    
    This is called when user selects files via the file browser.
    """
    if e.files:
        file_paths = [f.path for f in e.files if f.path]
        
        if file_paths:
            log_to_terminal(f"Archivos seleccionados: {len(file_paths)}", "info")
            asyncio.create_task(process_dropped_files(file_paths))


# =============================================================================
# MAIN APPLICATION ENTRY POINT
# =============================================================================

def main(page: ft.Page) -> None:
    """
    Main entry point for the Flet application.
    
    CRITICAL INITIALIZATION ORDER:
    1. Configure page settings
    2. Create FilePicker and add to page.overlay IMMEDIATELY
    3. Build UI (passing FilePicker reference)
    4. Add UI to page
    """
    
    # Store page reference
    APP.page = page
    
    # =========================================================================
    # STEP 1: Configure page
    # =========================================================================
    
    page.title = f"{CONFIG.APP_NAME} - {CONFIG.APP_SUBTITLE}"
    page.bgcolor = COLORS.BACKGROUND
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    # Window configuration (Flet 0.80+ syntax with fallback)
    try:
        page.window.width = CONFIG.WINDOW_WIDTH
        page.window.height = CONFIG.WINDOW_HEIGHT
        page.window.min_width = CONFIG.WINDOW_MIN_WIDTH
        page.window.min_height = CONFIG.WINDOW_MIN_HEIGHT
        # Don't call center() as it's async and not needed
    except AttributeError:
        # Fallback for older Flet versions
        try:
            page.window_width = CONFIG.WINDOW_WIDTH
            page.window_height = CONFIG.WINDOW_HEIGHT
            page.window_min_width = CONFIG.WINDOW_MIN_WIDTH
            page.window_min_height = CONFIG.WINDOW_MIN_HEIGHT
        except Exception as e:
            print(f"[WARNING] Could not configure window: {e}")
    
    # =========================================================================
    # STEP 2: Create FilePicker and add to overlay FIRST
    # =========================================================================
    
    # Create the FilePicker instance (no on_result in constructor for Flet 0.80+)
    file_picker = ft.FilePicker()

    # Set event handler AFTER creation
    file_picker.on_result = handle_file_picker_result

    # Store reference in controller
    APP.file_picker = file_picker
    
    # CRITICAL: Add to page.overlay BEFORE building any UI
    # This prevents the "Unknown control: FilePicker" red box error
    page.overlay.append(file_picker)
    
    # =========================================================================
    # STEP 3: Build UI (passing FilePicker as dependency)
    # =========================================================================
    
    # Build the complete UI, passing file_picker reference
    main_layout, ui_state = build_app_ui(
        page=page,
        file_picker=file_picker,
        on_execute=handle_execute_click,
    )
    
    # Store UI state in controller
    APP.ui_state = ui_state
    
    # =========================================================================
    # STEP 4: Add UI to page
    # =========================================================================
    
    page.add(main_layout)
    
    # Force initial update
    page.update()
    
    # =========================================================================
    # STEP 5: Initial logging
    # =========================================================================
    
    log_to_terminal("PRISMA iniciado correctamente", "success")
    log_to_terminal(f"Versión: {CONFIG.APP_VERSION}", "info")
    log_to_terminal("Esperando input...", "info")
    
    # Check module availability
    if not SCRAPER_AVAILABLE:
        log_to_terminal("⚠ Módulo scraper no disponible (modo mock)", "warning")
    if not ANALYZER_AVAILABLE:
        log_to_terminal("⚠ Módulo analyzer no disponible (modo mock)", "warning")
    
    # Final update
    page.update()


# =============================================================================
# APPLICATION STARTUP
# =============================================================================

if __name__ == "__main__":
    # Run the Flet application
    ft.app(target=main)