"""
PRISMA - Automated Research Desktop App
========================================
DIAGNOSTIC BUILD - FilePicker REMOVED

This is a minimal version to test the base layout.
All UI is inline, no external dependencies except Flet.

Author: PRISMA Team
Version: 2.1.0-diagnostic
"""

import asyncio
from datetime import datetime
from typing import List, Optional

import flet as ft


# =============================================================================
# THEME CONFIGURATION (INLINE)
# =============================================================================

class COLORS:
    """Color palette from PRISMA design spec."""
    BACKGROUND = "#0F1115"      # Charcoal Deep
    SURFACE = "#1E2129"         # Gunmetal
    SURFACE_LIGHT = "#2A2D37"   # Lighter surface for hover
    PRIMARY = "#8B5CF6"         # Electric Violet
    SUCCESS = "#10B981"         # Emerald Green
    ERROR = "#EF4444"           # Red
    WARNING = "#F59E0B"         # Amber
    TEXT_PRIMARY = "#F1F5F9"    # Off-white
    TEXT_SECONDARY = "#94A3B8"  # Slate (for logs)
    TEXT_MUTED = "#64748B"      # Muted text
    BORDER = "#374151"          # Border color


class CONFIG:
    """Application configuration."""
    APP_NAME = "PRISMA"
    APP_SUBTITLE = "Investigación Automatizada"
    APP_VERSION = "2.1.0-diagnostic"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 900
    WINDOW_MIN_HEIGHT = 600


# =============================================================================
# GLOBAL STATE (SIMPLIFIED)
# =============================================================================

class AppState:
    """Simple application state container."""
    
    def __init__(self):
        self.page: Optional[ft.Page] = None
        self.log_column: Optional[ft.Column] = None
        self.url_input: Optional[ft.TextField] = None
        self.url_counter: Optional[ft.Text] = None
        self.execute_btn: Optional[ft.ElevatedButton] = None
        self.ai_switch: Optional[ft.Switch] = None
        self.status_text: Optional[ft.Text] = None
        self.progress_bar: Optional[ft.ProgressBar] = None
        self.current_urls: List[str] = []


# Global state instance
STATE = AppState()


# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

def log_to_terminal(message: str, status: str = "info") -> None:
    """Add a log entry to the terminal display."""
    if STATE.log_column is None:
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
    
    STATE.log_column.controls.append(log_entry)
    
    # Limit log entries
    if len(STATE.log_column.controls) > 100:
        STATE.log_column.controls.pop(0)
    
    try:
        STATE.log_column.update()
    except Exception:
        pass


# =============================================================================
# EVENT HANDLERS (DUMMY - NO FILEPICKER)
# =============================================================================

def handle_file_button_click(e) -> None:
    """
    DUMMY HANDLER - FilePicker removed for diagnostic.
    Just prints to console.
    """
    print("Click dummy - FilePicker functionality disabled")
    log_to_terminal("Botón presionado (FilePicker deshabilitado)", "warning")


def handle_execute_click(e) -> None:
    """Handle execute button click."""
    print("Execute button clicked")
    log_to_terminal("Ejecutando proceso de prueba...", "info")
    
    # Simulate some work
    asyncio.create_task(mock_execution())


async def mock_execution() -> None:
    """Mock execution for testing UI responsiveness."""
    if STATE.execute_btn:
        STATE.execute_btn.disabled = True
        STATE.execute_btn.text = "PROCESANDO..."
        STATE.execute_btn.update()
    
    if STATE.progress_bar:
        STATE.progress_bar.visible = True
        STATE.progress_bar.update()
    
    # Simulate phases
    for i in range(5):
        await asyncio.sleep(0.5)
        log_to_terminal(f"Paso {i+1}/5 completado", "success")
        
        if STATE.progress_bar:
            STATE.progress_bar.value = (i + 1) / 5
            STATE.progress_bar.update()
    
    log_to_terminal("Proceso de prueba completado", "success")
    
    if STATE.execute_btn:
        STATE.execute_btn.disabled = False
        STATE.execute_btn.text = "EJECUTAR INVESTIGACIÓN"
        STATE.execute_btn.update()


def handle_ai_switch_change(e) -> None:
    """Handle AI switch toggle."""
    is_enabled = e.control.value
    status = "activado" if is_enabled else "desactivado"
    log_to_terminal(f"Análisis IA {status}", "ai" if is_enabled else "info")


def handle_url_input_change(e) -> None:
    """Handle URL input changes."""
    text = e.control.value or ""
    # Count URLs (simple pattern)
    import re
    urls = re.findall(r'https?://[^\s]+', text)
    count = len(urls)
    
    if STATE.url_counter:
        STATE.url_counter.value = f"{count} URL(s) detectadas"
        STATE.url_counter.update()


# =============================================================================
# UI COMPONENTS (INLINE)
# =============================================================================

def build_header() -> ft.Container:
    """Build the application header."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.AUTO_AWESOME,
                    color=COLORS.PRIMARY,
                    size=28,
                ),
                ft.Text(
                    CONFIG.APP_NAME,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS.TEXT_PRIMARY,
                ),
                ft.Text(
                    CONFIG.APP_SUBTITLE,
                    size=14,
                    color=COLORS.TEXT_SECONDARY,
                ),
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=COLORS.SURFACE,
    )


def build_input_section() -> ft.Container:
    """
    Build the input section (left panel).
    FIXED DIMENSIONS for diagnostic.
    """
    # File button (DUMMY - no FilePicker)
    file_button = ft.ElevatedButton(
        text="Seleccionar Archivos",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=handle_file_button_click,  # DUMMY HANDLER
        style=ft.ButtonStyle(
            color=COLORS.TEXT_PRIMARY,
            bgcolor=COLORS.SURFACE_LIGHT,
        ),
        width=220,
        height=45,
    )
    
    # URL input field
    url_input = ft.TextField(
        hint_text="O pega URLs aquí (una por línea)...",
        multiline=True,
        min_lines=5,
        max_lines=10,
        border_color=COLORS.BORDER,
        focused_border_color=COLORS.PRIMARY,
        cursor_color=COLORS.PRIMARY,
        text_style=ft.TextStyle(
            color=COLORS.TEXT_PRIMARY,
            font_family="Consolas",
            size=12,
        ),
        hint_style=ft.TextStyle(
            color=COLORS.TEXT_MUTED,
            size=12,
        ),
        on_change=handle_url_input_change,
    )
    STATE.url_input = url_input
    
    # URL counter
    url_counter = ft.Text(
        "0 URL(s) detectadas",
        size=12,
        color=COLORS.TEXT_MUTED,
    )
    STATE.url_counter = url_counter
    
    # Drop zone visual (static, no drag-drop for now)
    drop_zone = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    name=ft.Icons.CLOUD_UPLOAD,
                    size=48,
                    color=COLORS.TEXT_MUTED,
                ),
                ft.Text(
                    "Arrastra archivos .txt o .docx",
                    size=14,
                    color=COLORS.TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "(Drag & Drop deshabilitado en diagnóstico)",
                    size=11,
                    color=COLORS.TEXT_MUTED,
                    italic=True,
                ),
                ft.Container(height=10),
                file_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        border=ft.border.all(2, COLORS.BORDER),
        border_radius=12,
        padding=24,
        bgcolor=COLORS.SURFACE,
        # FIXED DIMENSIONS
        height=200,
    )
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "ENTRADA DE DATOS",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS.TEXT_MUTED,
                ),
                ft.Container(height=8),
                drop_zone,
                ft.Container(height=16),
                url_input,
                ft.Container(height=4),
                url_counter,
            ],
            spacing=0,
        ),
        padding=16,
        bgcolor=COLORS.BACKGROUND,
        border_radius=8,
        border=ft.border.all(1, COLORS.BORDER),
        # FIXED DIMENSIONS for diagnostic
        width=500,
        height=500,
    )


def build_terminal_section() -> ft.Container:
    """
    Build the terminal/log section (right panel).
    FIXED DIMENSIONS for diagnostic.
    """
    # Log column (scrollable)
    log_column = ft.Column(
        controls=[],
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        auto_scroll=True,
    )
    STATE.log_column = log_column
    
    # Terminal header
    terminal_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    "TERMINAL",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS.TEXT_MUTED,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=COLORS.TEXT_MUTED,
                    icon_size=18,
                    tooltip="Limpiar terminal",
                    on_click=lambda e: log_column.controls.clear() or log_column.update(),
                ),
            ],
        ),
        padding=ft.padding.only(bottom=8),
    )
    
    # Terminal content area
    terminal_content = ft.Container(
        content=log_column,
        bgcolor="#0A0C0F",  # Darker than background
        border_radius=8,
        padding=16,
        # Let it fill available space within fixed container
        expand=True,
    )
    
    return ft.Container(
        content=ft.Column(
            controls=[
                terminal_header,
                terminal_content,
            ],
            spacing=0,
            expand=True,  # This expand is OK inside fixed container
        ),
        padding=16,
        bgcolor=COLORS.SURFACE,
        border_radius=8,
        border=ft.border.all(1, COLORS.BORDER),
        # FIXED DIMENSIONS for diagnostic
        width=500,
        height=500,
    )


def build_control_panel() -> ft.Container:
    """Build the bottom control panel."""
    # AI Switch
    ai_switch = ft.Switch(
        label="Análisis con IA",
        value=False,
        active_color=COLORS.PRIMARY,
        on_change=handle_ai_switch_change,
    )
    STATE.ai_switch = ai_switch
    
    # Execute button
    execute_btn = ft.ElevatedButton(
        text="EJECUTAR INVESTIGACIÓN",
        icon=ft.Icons.PLAY_ARROW,
        on_click=handle_execute_click,
        style=ft.ButtonStyle(
            color=COLORS.TEXT_PRIMARY,
            bgcolor=COLORS.PRIMARY,
            padding=ft.padding.symmetric(horizontal=32, vertical=16),
        ),
        height=56,
    )
    STATE.execute_btn = execute_btn
    
    # Progress bar
    progress_bar = ft.ProgressBar(
        value=0,
        color=COLORS.PRIMARY,
        bgcolor=COLORS.SURFACE_LIGHT,
        visible=False,
    )
    STATE.progress_bar = progress_bar
    
    # Status text
    status_text = ft.Text(
        f"Listo | v{CONFIG.APP_VERSION}",
        size=11,
        color=COLORS.TEXT_MUTED,
    )
    STATE.status_text = status_text
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ai_switch,
                        ft.Container(expand=True),
                        execute_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=12),
                progress_bar,
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        status_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=0,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=COLORS.SURFACE,
    )


def build_main_layout() -> ft.Column:
    """
    Build the complete application layout.
    
    Structure:
    - Header (top bar)
    - Content Row (input + terminal) with FIXED sizes
    - Control Panel (bottom)
    """
    # Build sections
    header = build_header()
    input_section = build_input_section()
    terminal_section = build_terminal_section()
    control_panel = build_control_panel()
    
    # Main content row with FIXED size containers
    content_row = ft.Row(
        controls=[
            input_section,
            terminal_section,
        ],
        spacing=16,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
    
    # Wrap content in scrollable container for smaller screens
    content_wrapper = ft.Container(
        content=content_row,
        padding=16,
    )
    
    # Main layout
    main_layout = ft.Column(
        controls=[
            header,
            ft.Container(
                content=content_wrapper,
                expand=True,
            ),
            control_panel,
        ],
        spacing=0,
        expand=True,
    )
    
    return main_layout


# =============================================================================
# MAIN APPLICATION ENTRY POINT
# =============================================================================

def main(page: ft.Page) -> None:
    """
    Main entry point for the Flet application.
    
    DIAGNOSTIC VERSION:
    - NO FilePicker
    - NO page.overlay
    - FIXED dimensions for layout testing
    """
    
    # Store page reference
    STATE.page = page
    
    # =========================================================================
    # STEP 1: Configure page
    # =========================================================================
    
    page.title = f"{CONFIG.APP_NAME} - {CONFIG.APP_SUBTITLE}"
    page.bgcolor = COLORS.BACKGROUND
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    # Window configuration
    try:
        # Flet 0.21+ syntax
        page.window.width = CONFIG.WINDOW_WIDTH
        page.window.height = CONFIG.WINDOW_HEIGHT
        page.window.min_width = CONFIG.WINDOW_MIN_WIDTH
        page.window.min_height = CONFIG.WINDOW_MIN_HEIGHT
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
    # STEP 2: Build UI (NO FilePicker involved)
    # =========================================================================
    
    main_layout = build_main_layout()
    
    # =========================================================================
    # STEP 3: Add UI to page
    # =========================================================================
    
    page.add(main_layout)
    page.update()
    
    # =========================================================================
    # STEP 4: Initial logging
    # =========================================================================
    
    log_to_terminal("PRISMA iniciado correctamente", "success")
    log_to_terminal(f"Versión: {CONFIG.APP_VERSION} (diagnóstico)", "info")
    log_to_terminal("FilePicker DESHABILITADO para pruebas", "warning")
    log_to_terminal("Esperando input...", "info")
    
    page.update()


# =============================================================================
# APPLICATION STARTUP
# =============================================================================

if __name__ == "__main__":
    ft.app(target=main)