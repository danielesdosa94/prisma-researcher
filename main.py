"""
PRISMA - Automated Research Desktop App (MONOLITHIC VERSION)
=============================================================
Single-file implementation to debug UI rendering issues in Flet 0.80.2

PROBLEM SOLVED: expand=True in nested custom classes causes height collapse.
SOLUTION: Use functions instead of class inheritance, explicit dimensions.

Author: PRISMA Team
Version: 1.0.0-monolith
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
import flet as ft

# =============================================================================
# THEME CONSTANTS (Inline - No imports)
# =============================================================================

class Colors:
    """PRISMA color palette - Dark/Violet aesthetic."""
    BACKGROUND = "#0F1115"
    SURFACE = "#1E2129"
    SURFACE_HOVER = "#282D38"
    SURFACE_BORDER = "#2D333D"
    PRIMARY = "#8B5CF6"
    PRIMARY_HOVER = "#A78BFA"
    PRIMARY_DIM = "#6D28D9"
    SUCCESS = "#10B981"
    ERROR = "#EF4444"
    WARNING = "#F59E0B"
    TEXT_PRIMARY = "#F1F5F9"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"
    TEXT_ON_PRIMARY = "#FFFFFF"
    TERMINAL_BG = "#0A0C0F"


class Config:
    """Application configuration."""
    APP_NAME = "PRISMA"
    APP_SUBTITLE = "Investigación Automatizada"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 900
    WINDOW_MIN_HEIGHT = 600


# =============================================================================
# GLOBAL STATE (Simple approach for monolith)
# =============================================================================

class AppState:
    """Global application state."""
    current_urls: List[str] = []
    is_processing: bool = False
    log_column: Optional[ft.Column] = None
    url_counter: Optional[ft.Text] = None
    execute_btn: Optional[ft.Container] = None
    ai_switch: Optional[ft.Switch] = None
    url_input: Optional[ft.TextField] = None
    report_btn: Optional[ft.Container] = None
    file_picker: Optional[ft.FilePicker] = None


STATE = AppState()


# =============================================================================
# LOGGING FUNCTIONS (Inline)
# =============================================================================

def log_to_terminal(message: str, status: str = "info") -> None:
    """Add a log entry to the terminal."""
    if STATE.log_column is None:
        print(f"[{status.upper()}] {message}")
        return
    
    color_map = {
        "info": Colors.TEXT_SECONDARY,
        "success": Colors.SUCCESS,
        "error": Colors.ERROR,
        "warning": Colors.WARNING,
        "ai": Colors.PRIMARY,
    }
    color = color_map.get(status, Colors.TEXT_SECONDARY)
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    log_row = ft.Row(
        controls=[
            ft.Text(
                f"[{timestamp}]",
                color=Colors.TEXT_MUTED,
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
    
    STATE.log_column.controls.append(log_row)
    
    # Limit log entries
    if len(STATE.log_column.controls) > 200:
        STATE.log_column.controls.pop(0)
    
    try:
        STATE.log_column.update()
    except Exception:
        pass


# =============================================================================
# FILE HANDLING FUNCTIONS (Simplified/Mock)
# =============================================================================

def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text content."""
    import re
    url_pattern = r'https?://[^\s<>"\')\]]+|www\.[^\s<>"\')\]]+'
    urls = re.findall(url_pattern, text)
    # Add https:// to www URLs
    urls = [f"https://{url}" if url.startswith("www.") else url for url in urls]
    return list(set(urls))


async def read_file_content(file_path: str) -> str:
    """Read file content (simplified)."""
    path = Path(file_path)
    try:
        if path.suffix.lower() == '.txt':
            return path.read_text(encoding='utf-8')
        elif path.suffix.lower() == '.docx':
            # Mock for now - would need python-docx
            return f"[Contenido de {path.name}]"
        else:
            return ""
    except Exception as e:
        log_to_terminal(f"Error leyendo {path.name}: {e}", "error")
        return ""


# =============================================================================
# UI COMPONENT FACTORY FUNCTIONS
# =============================================================================

def create_prisma_button(
    text: str,
    icon: Optional[str] = None,
    variant: str = "primary",
    on_click: Optional[Callable] = None,
    disabled: bool = False,
    expand: bool = False,
) -> ft.Container:
    """Create a styled button without class inheritance issues."""
    
    if variant == "primary":
        bg_color = Colors.PRIMARY
        text_color = Colors.TEXT_ON_PRIMARY
        hover_color = Colors.PRIMARY_HOVER
    elif variant == "secondary":
        bg_color = Colors.SURFACE
        text_color = Colors.TEXT_PRIMARY
        hover_color = Colors.SURFACE_HOVER
    else:
        bg_color = "transparent"
        text_color = Colors.TEXT_SECONDARY
        hover_color = Colors.SURFACE_HOVER
    
    if disabled:
        bg_color = Colors.SURFACE
        text_color = Colors.TEXT_MUTED
    
    # Build content
    content_controls = []
    if icon:
        content_controls.append(
            ft.Icon(icon, size=18, color=text_color)
        )
    content_controls.append(
        ft.Text(text, size=14, weight=ft.FontWeight.W_500, color=text_color)
    )
    
    btn = ft.Container(
        content=ft.Row(
            controls=content_controls,
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
        bgcolor=bg_color,
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        height=48,
        expand=expand,
        ink=not disabled,
    )
    
    # Store colors for hover effect
    btn.data = {"bg": bg_color, "hover": hover_color, "disabled": disabled}
    
    # Assign events AFTER creation
    if on_click and not disabled:
        btn.on_click = on_click
    
    if not disabled:
        def handle_hover(e):
            if btn.data.get("disabled"):
                return
            btn.bgcolor = btn.data["hover"] if e.data == "true" else btn.data["bg"]
            btn.update()
        btn.on_hover = handle_hover
    
    return btn


def create_header_section() -> ft.Container:
    """Create the header section."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon("auto_awesome", size=32, color=Colors.PRIMARY),
                    bgcolor=Colors.SURFACE,
                    border_radius=8,
                    padding=8,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            Config.APP_NAME,
                            size=24,
                            weight=ft.FontWeight.W_700,
                            color=Colors.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            Config.APP_SUBTITLE,
                            size=12,
                            color=Colors.TEXT_SECONDARY,
                        ),
                    ],
                    spacing=0,
                ),
            ],
            spacing=16,
        ),
        bgcolor=Colors.BACKGROUND,
        padding=ft.padding.only(left=24, right=24, top=16, bottom=8),
        height=80,  # FIXED HEIGHT
    )


def create_input_section(page: ft.Page) -> ft.Container:
    """Create the input/drag-drop section."""
    
    # File picker - create empty first
    STATE.file_picker = ft.FilePicker()
    
    # URL input field
    STATE.url_input = ft.TextField(
        hint_text="Pega URLs aquí (una por línea)...",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_color=Colors.SURFACE_BORDER,
        focused_border_color=Colors.PRIMARY,
        bgcolor=Colors.SURFACE,
        color=Colors.TEXT_PRIMARY,
        cursor_color=Colors.PRIMARY,
        hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
        border_radius=8,
        text_size=12,
    )
    
    # Browse button
    browse_btn = create_prisma_button(
        text="Seleccionar Archivos",
        icon="folder_open_rounded",
        variant="secondary",
    )
    
    # URL counter
    STATE.url_counter = ft.Text(
        "0 enlaces detectados",
        size=12,
        color=Colors.TEXT_SECONDARY,
    )
    
    # Build the drag-drop zone content
    drag_zone = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon("upload_file_rounded", size=48, color=Colors.TEXT_MUTED),
                ft.Text(
                    "Arrastra archivos .txt o .docx aquí",
                    color=Colors.TEXT_SECONDARY,
                    size=14,
                ),
                ft.Container(height=10),
                browse_btn,
                ft.Container(height=10),
                ft.Text(
                    "— o pega URLs directamente —",
                    size=12,
                    color=Colors.TEXT_MUTED,
                ),
                STATE.url_input,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        bgcolor=Colors.SURFACE,
        border=ft.border.all(2, Colors.SURFACE_BORDER),
        border_radius=12,
        padding=24,
        expand=True,  # Expand within fixed-height parent
    )
    
    # Connect file picker events AFTER creation
    def handle_file_result(e: ft.ControlEvent):
        if e.files:
            file_paths = [f.path for f in e.files]
            log_to_terminal(f"Archivos recibidos: {len(file_paths)}", "info")
            asyncio.create_task(process_dropped_files(file_paths))
    
    STATE.file_picker.on_result = handle_file_result
    browse_btn.on_click = lambda _: STATE.file_picker.pick_files(
        allow_multiple=True,
        allowed_extensions=["txt", "docx"],
    )
    
    # Full input section
    input_section = ft.Container(
        content=ft.Column(
            controls=[
                STATE.file_picker,  # Hidden file picker
                ft.Text(
                    "ENTRADA",
                    size=11,
                    weight=ft.FontWeight.W_600,
                    color=Colors.TEXT_MUTED,
                ),
                drag_zone,
                ft.Row(
                    controls=[
                        ft.Icon("link_rounded", size=16, color=Colors.TEXT_SECONDARY),
                        STATE.url_counter,
                    ],
                    spacing=8,
                ),
            ],
            spacing=10,
        ),
        bgcolor=Colors.BACKGROUND,
        padding=16,
        width=500,  # FIXED WIDTH instead of expand
    )
    
    return input_section


def create_terminal_section() -> ft.Container:
    """Create the terminal/log section."""
    
    # Log column with auto-scroll
    STATE.log_column = ft.Column(
        controls=[],
        spacing=2,
        scroll=ft.ScrollMode.AUTO,
        auto_scroll=True,
    )
    
    # Terminal container
    terminal = ft.Container(
        content=STATE.log_column,
        bgcolor=Colors.TERMINAL_BG,
        border_radius=8,
        border=ft.border.all(1, Colors.SURFACE_BORDER),
        padding=16,
        expand=True,  # Expand within fixed container
    )
    
    # Report button (hidden initially)
    STATE.report_btn = create_prisma_button(
        text="Ver Reporte",
        icon="description_rounded",
        variant="secondary",
        expand=True,
    )
    STATE.report_btn.visible = False
    
    # Full terminal section
    terminal_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "TERMINAL",
                    size=11,
                    weight=ft.FontWeight.W_600,
                    color=Colors.TEXT_MUTED,
                ),
                terminal,
                STATE.report_btn,
            ],
            spacing=10,
        ),
        bgcolor=Colors.BACKGROUND,
        padding=16,
        expand=1,  # Use expand=1 (integer) instead of True
    )
    
    return terminal_section


def create_control_panel(on_execute: Callable) -> ft.Container:
    """Create the bottom control panel."""
    
    # AI Switch
    STATE.ai_switch = ft.Switch(
        value=False,
        active_color=Colors.PRIMARY,
        inactive_track_color=Colors.SURFACE_BORDER,
    )
    
    ai_switch_row = ft.Container(
        content=ft.Row(
            controls=[
                STATE.ai_switch,
                ft.Text(
                    "Análisis con IA",
                    color=Colors.TEXT_PRIMARY,
                    size=14,
                ),
            ],
            spacing=8,
        ),
        padding=ft.padding.symmetric(vertical=8),
    )
    
    # Execute button
    STATE.execute_btn = create_prisma_button(
        text="EJECUTAR INVESTIGACIÓN",
        icon="rocket_launch_rounded",
        variant="primary",
        expand=True,
    )
    STATE.execute_btn.on_click = lambda _: on_execute()
    
    # Control panel container
    control_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[ai_switch_row],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                STATE.execute_btn,
            ],
            spacing=16,
        ),
        bgcolor=Colors.SURFACE,
        padding=24,
        border=ft.border.only(top=ft.BorderSide(1, Colors.SURFACE_BORDER)),
        height=120,  # FIXED HEIGHT
    )
    
    return control_panel


def create_status_bar() -> ft.Container:
    """Create the bottom status bar."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon("circle", size=8, color=Colors.SUCCESS),
                ft.Text(
                    "Listo",
                    size=12,
                    color=Colors.TEXT_MUTED,
                ),
                ft.Container(expand=True),
                ft.Text(
                    f"{Config.APP_NAME} v1.0.0",
                    size=11,
                    color=Colors.TEXT_MUTED,
                ),
            ],
            spacing=8,
        ),
        bgcolor=Colors.BACKGROUND,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        border=ft.border.only(top=ft.BorderSide(1, Colors.SURFACE_BORDER)),
        height=36,  # FIXED HEIGHT
    )


# =============================================================================
# MAIN LAYOUT BUILDER (Function, not class!)
# =============================================================================

def build_main_layout(page: ft.Page, on_execute: Callable) -> ft.Container:
    """
    Build the complete main layout using functions instead of nested classes.
    This avoids the expand=True inheritance bug in Flet 0.80.2.
    """
    
    # Create all sections
    header = create_header_section()
    input_section = create_input_section(page)
    terminal_section = create_terminal_section()
    control_panel = create_control_panel(on_execute)
    status_bar = create_status_bar()
    
    # Main content area (Input + Terminal side by side)
    # Using FIXED widths and calculated heights instead of expand chains
    main_content = ft.Container(
        content=ft.Row(
            controls=[
                input_section,
                ft.VerticalDivider(width=1, color=Colors.SURFACE_BORDER),
                terminal_section,
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        expand=True,  # Only ONE expand=True at this level
        bgcolor=Colors.BACKGROUND,
    )
    
    # Full layout column
    main_layout = ft.Container(
        content=ft.Column(
            controls=[
                header,
                ft.Divider(height=1, color=Colors.SURFACE_BORDER),
                main_content,
                control_panel,
                status_bar,
            ],
            spacing=0,
            expand=True,
        ),
        bgcolor=Colors.BACKGROUND,
        expand=True,
    )
    
    return main_layout


# =============================================================================
# APPLICATION LOGIC
# =============================================================================

async def process_dropped_files(file_paths: List[str]) -> None:
    """Process dropped files and extract URLs."""
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
            log_to_terminal(f"Error: {e}", "error")
    
    # Update state
    STATE.current_urls = list(set(all_urls))
    
    # Update counter
    if STATE.url_counter:
        STATE.url_counter.value = f"{len(STATE.current_urls)} enlaces detectados"
        STATE.url_counter.update()
    
    if STATE.current_urls:
        log_to_terminal(
            f"✓ {len(STATE.current_urls)} URLs válidas en total",
            "success"
        )


async def execute_pipeline() -> None:
    """Execute the scraping/analysis pipeline (MOCK for UI testing)."""
    
    if STATE.is_processing:
        return
    
    # Get URLs from text input
    if STATE.url_input and STATE.url_input.value:
        manual_urls = extract_urls_from_text(STATE.url_input.value)
        STATE.current_urls.extend(manual_urls)
        STATE.current_urls = list(set(STATE.current_urls))
    
    if not STATE.current_urls:
        log_to_terminal("No hay URLs para procesar", "warning")
        return
    
    STATE.is_processing = True
    
    # Update button state
    if STATE.execute_btn:
        STATE.execute_btn.data["disabled"] = True
        STATE.execute_btn.bgcolor = Colors.SURFACE
        # Update text
        btn_content = STATE.execute_btn.content
        if isinstance(btn_content, ft.Row) and len(btn_content.controls) > 1:
            text_ctrl = btn_content.controls[-1]
            if isinstance(text_ctrl, ft.Text):
                text_ctrl.value = "PROCESANDO..."
                text_ctrl.color = Colors.TEXT_MUTED
        STATE.execute_btn.update()
    
    try:
        use_ai = STATE.ai_switch.value if STATE.ai_switch else False
        
        # Phase 1: Scraping (MOCK)
        log_to_terminal("═" * 40, "info")
        log_to_terminal("FASE 1: SCRAPING", "info")
        log_to_terminal("═" * 40, "info")
        
        for i, url in enumerate(STATE.current_urls, 1):
            domain = url.split('/')[2] if '/' in url else url[:30]
            log_to_terminal(f"[{i}/{len(STATE.current_urls)}] Scrapeando: {domain}...", "info")
            await asyncio.sleep(0.5)  # Simulate work
            log_to_terminal(f"  → Completado (mock)", "success")
        
        log_to_terminal(
            f"✓ {len(STATE.current_urls)}/{len(STATE.current_urls)} páginas scrapeadas",
            "success"
        )
        
        # Phase 2: AI Analysis (MOCK)
        if use_ai:
            log_to_terminal("═" * 40, "ai")
            log_to_terminal("FASE 2: ANÁLISIS IA", "ai")
            log_to_terminal("═" * 40, "ai")
            
            log_to_terminal("Cargando modelo...", "ai")
            await asyncio.sleep(1)
            
            log_to_terminal("Analizando contenido...", "ai")
            await asyncio.sleep(1.5)
            
            log_to_terminal("Generando informe...", "ai")
            await asyncio.sleep(1)
            
            log_to_terminal("✓ Reporte generado: report_20260122.md", "success")
            
            # Show report button
            if STATE.report_btn:
                STATE.report_btn.visible = True
                STATE.report_btn.update()
        
        # Completion
        log_to_terminal("═" * 40, "success")
        log_to_terminal("✓ PROCESO COMPLETADO", "success")
        log_to_terminal("═" * 40, "success")
        
    except Exception as e:
        log_to_terminal(f"Error: {e}", "error")
    
    finally:
        STATE.is_processing = False
        
        # Reset button
        if STATE.execute_btn:
            STATE.execute_btn.data["disabled"] = False
            STATE.execute_btn.bgcolor = Colors.PRIMARY
            btn_content = STATE.execute_btn.content
            if isinstance(btn_content, ft.Row) and len(btn_content.controls) > 1:
                text_ctrl = btn_content.controls[-1]
                if isinstance(text_ctrl, ft.Text):
                    text_ctrl.value = "EJECUTAR INVESTIGACIÓN"
                    text_ctrl.color = Colors.TEXT_ON_PRIMARY
            STATE.execute_btn.update()


def handle_execute():
    """Handle execute button click."""
    asyncio.create_task(execute_pipeline())


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main(page: ft.Page) -> None:
    """Main entry point for Flet application."""
    
    # Configure page
    page.title = f"{Config.APP_NAME} - {Config.APP_SUBTITLE}"
    page.bgcolor = Colors.BACKGROUND
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    # Window settings
    try:
        page.window.width = Config.WINDOW_WIDTH
        page.window.height = Config.WINDOW_HEIGHT
        page.window.min_width = Config.WINDOW_MIN_WIDTH
        page.window.min_height = Config.WINDOW_MIN_HEIGHT
    except AttributeError:
        # Fallback for older Flet versions
        try:
            page.window_width = Config.WINDOW_WIDTH
            page.window_height = Config.WINDOW_HEIGHT
            page.window_min_width = Config.WINDOW_MIN_WIDTH
            page.window_min_height = Config.WINDOW_MIN_HEIGHT
        except Exception as e:
            print(f"Warning: Could not set window size: {e}")
    
    # Build and add layout
    layout = build_main_layout(page, handle_execute)
    page.add(layout)
    
    # Force update
    page.update()
    
    # Initial log
    log_to_terminal("PRISMA iniciado correctamente", "success")
    log_to_terminal("Esperando input...", "info")
    
    # Final update
    page.update()


if __name__ == "__main__":
    ft.app(target=main)