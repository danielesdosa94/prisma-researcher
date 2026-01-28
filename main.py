"""
PRISMA - Automated Research Desktop App
========================================
DIAGNOSTIC BUILD - STABLE VERSION 2.1.4

Fixes applied:
1. COLORS: Added missing 'TEXT_ON_PRIMARY' attribute.
2. Buttons: Uses 'content' property (universal compatibility).
3. Icons: Uses positional arguments.

Author: PRISMA Team
Version: 2.1.4-stable
"""

import asyncio
from datetime import datetime
from typing import List, Optional

import flet as ft


# =============================================================================
# THEME CONFIGURATION
# =============================================================================

class COLORS:
    BACKGROUND = "#0F1115"
    SURFACE = "#1E2129"
    SURFACE_LIGHT = "#2A2D37"
    PRIMARY = "#8B5CF6"
    SUCCESS = "#10B981"
    ERROR = "#EF4444"
    WARNING = "#F59E0B"
    TEXT_PRIMARY = "#F1F5F9"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"
    BORDER = "#374151"
    # FIX: Agregado el color que faltaba
    TEXT_ON_PRIMARY = "#FFFFFF" 


class CONFIG:
    APP_NAME = "PRISMA"
    APP_SUBTITLE = "Investigación Automatizada"
    APP_VERSION = "2.1.4"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 900
    WINDOW_MIN_HEIGHT = 600


# =============================================================================
# GLOBAL STATE
# =============================================================================

class AppState:
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

STATE = AppState()


# =============================================================================
# LOGGING
# =============================================================================

def log_to_terminal(message: str, status: str = "info") -> None:
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
            ft.Text(f"[{timestamp}]", color=COLORS.TEXT_MUTED, size=11, font_family="Consolas"),
            ft.Text(f"> {message}", color=color, size=13, font_family="Consolas", selectable=True),
        ],
        spacing=8,
    )
    
    STATE.log_column.controls.append(log_entry)
    if len(STATE.log_column.controls) > 100:
        STATE.log_column.controls.pop(0)
    
    try: STATE.log_column.update()
    except: pass


# =============================================================================
# HANDLERS
# =============================================================================

def handle_file_button_click(e) -> None:
    print("Click dummy - FilePicker disabled")
    log_to_terminal("Botón presionado (FilePicker deshabilitado)", "warning")

def handle_execute_click(e) -> None:
    print("Execute button clicked")
    log_to_terminal("Ejecutando proceso de prueba...", "info")
    asyncio.create_task(mock_execution())

async def mock_execution() -> None:
    if STATE.execute_btn:
        STATE.execute_btn.disabled = True
        # Actualizar texto manualmente accediendo al contenido
        # controls[1] es el Texto dentro del Row del botón
        STATE.execute_btn.content.controls[1].value = "PROCESANDO..."
        STATE.execute_btn.update()
    
    if STATE.progress_bar:
        STATE.progress_bar.visible = True
        STATE.progress_bar.update()
    
    for i in range(5):
        await asyncio.sleep(0.5)
        log_to_terminal(f"Paso {i+1}/5 completado", "success")
        if STATE.progress_bar:
            STATE.progress_bar.value = (i + 1) / 5
            STATE.progress_bar.update()
    
    log_to_terminal("Proceso de prueba completado", "success")
    
    if STATE.execute_btn:
        STATE.execute_btn.disabled = False
        STATE.execute_btn.content.controls[1].value = "EJECUTAR INVESTIGACIÓN"
        STATE.execute_btn.update()

def handle_ai_switch_change(e) -> None:
    is_enabled = e.control.value
    status = "activado" if is_enabled else "desactivado"
    log_to_terminal(f"Análisis IA {status}", "ai" if is_enabled else "info")

def handle_url_input_change(e) -> None:
    text = e.control.value or ""
    import re
    urls = re.findall(r'https?://[^\s]+', text)
    count = len(urls)
    if STATE.url_counter:
        STATE.url_counter.value = f"{count} URL(s) detectadas"
        STATE.url_counter.update()


# =============================================================================
# UI BUILDERS (SAFE MODE)
# =============================================================================

def build_header() -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon("auto_awesome", color=COLORS.PRIMARY, size=28),
                ft.Text(CONFIG.APP_NAME, size=24, weight=ft.FontWeight.BOLD, color=COLORS.TEXT_PRIMARY),
                ft.Text(CONFIG.APP_SUBTITLE, size=14, color=COLORS.TEXT_SECONDARY),
            ],
            spacing=12,
        ),
        padding=ft.Padding(left=24, right=24, top=16, bottom=16),
        bgcolor=COLORS.SURFACE,
    )

def build_input_section() -> ft.Container:
    # BOTÓN SEGURO: Usamos 'content' en lugar de 'text'/'icon'
    file_button_content = ft.Row(
        controls=[
            ft.Icon("upload_file", color=COLORS.TEXT_PRIMARY),
            ft.Text("Seleccionar Archivos", color=COLORS.TEXT_PRIMARY),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    file_button = ft.ElevatedButton(
        content=file_button_content,
        on_click=handle_file_button_click,
        style=ft.ButtonStyle(
            color=COLORS.TEXT_PRIMARY,
            bgcolor=COLORS.SURFACE_LIGHT,
        ),
        width=220,
        height=45,
    )
    
    url_input = ft.TextField(
        hint_text="O pega URLs aquí...",
        multiline=True,
        min_lines=5,
        max_lines=10,
        border_color=COLORS.BORDER,
        focused_border_color=COLORS.PRIMARY,
        cursor_color=COLORS.PRIMARY,
        text_style=ft.TextStyle(color=COLORS.TEXT_PRIMARY, font_family="Consolas", size=12),
        hint_style=ft.TextStyle(color=COLORS.TEXT_MUTED, size=12),
        on_change=handle_url_input_change,
    )
    STATE.url_input = url_input
    
    url_counter = ft.Text("0 URL(s) detectadas", size=12, color=COLORS.TEXT_MUTED)
    STATE.url_counter = url_counter
    
    drop_zone = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon("cloud_upload", size=48, color=COLORS.TEXT_MUTED),
                ft.Text("Arrastra archivos .txt o .docx", size=14, color=COLORS.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                file_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        border=ft.Border.all(2, COLORS.BORDER),
        border_radius=12,
        padding=24,
        bgcolor=COLORS.SURFACE,
        height=200,
    )
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("ENTRADA DE DATOS", size=12, weight=ft.FontWeight.BOLD, color=COLORS.TEXT_MUTED),
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
        border=ft.Border.all(1, COLORS.BORDER),
        width=500,
        height=500,
    )

def build_terminal_section() -> ft.Container:
    log_column = ft.Column(controls=[], spacing=4, scroll=ft.ScrollMode.AUTO, auto_scroll=True)
    STATE.log_column = log_column
    
    terminal_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("TERMINAL", size=12, weight=ft.FontWeight.BOLD, color=COLORS.TEXT_MUTED),
                ft.Container(expand=True),
                # IconButton seguro
                ft.IconButton(
                    icon="delete_outline",
                    icon_color=COLORS.TEXT_MUTED,
                    icon_size=18,
                    tooltip="Limpiar terminal",
                    on_click=lambda e: log_column.controls.clear() or log_column.update(),
                ),
            ],
        ),
        padding=ft.Padding(left=0, top=0, right=0, bottom=8),
    )
    
    terminal_content = ft.Container(
        content=log_column,
        bgcolor="#0A0C0F",
        border_radius=8,
        padding=16,
        expand=True,
    )
    
    return ft.Container(
        content=ft.Column(
            controls=[terminal_header, terminal_content],
            spacing=0,
            expand=True,
        ),
        padding=16,
        bgcolor=COLORS.SURFACE,
        border_radius=8,
        border=ft.Border.all(1, COLORS.BORDER),
        width=500,
        height=500,
    )

def build_control_panel() -> ft.Container:
    ai_switch = ft.Switch(
        label="Análisis con IA",
        value=False,
        active_color=COLORS.PRIMARY,
        on_change=handle_ai_switch_change,
    )
    STATE.ai_switch = ai_switch
    
    # BOTÓN DE EJECUCIÓN SEGURO
    execute_btn_content = ft.Row(
        controls=[
            ft.Icon("play_arrow", color=COLORS.TEXT_ON_PRIMARY),
            ft.Text("EJECUTAR INVESTIGACIÓN", color=COLORS.TEXT_ON_PRIMARY, weight=ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    execute_btn = ft.ElevatedButton(
        content=execute_btn_content,
        on_click=handle_execute_click,
        style=ft.ButtonStyle(
            color=COLORS.TEXT_PRIMARY,
            bgcolor=COLORS.PRIMARY,
            padding=ft.Padding(left=32, top=16, right=32, bottom=16),
        ),
        height=56,
    )
    STATE.execute_btn = execute_btn
    
    progress_bar = ft.ProgressBar(value=0, color=COLORS.PRIMARY, bgcolor=COLORS.SURFACE_LIGHT, visible=False)
    STATE.progress_bar = progress_bar
    
    status_text = ft.Text(f"Listo | v{CONFIG.APP_VERSION}", size=11, color=COLORS.TEXT_MUTED)
    STATE.status_text = status_text
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[ai_switch, ft.Container(expand=True), execute_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=12),
                progress_bar,
                ft.Container(height=8),
                ft.Row(controls=[status_text], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=0,
        ),
        padding=ft.Padding(left=24, top=16, right=24, bottom=16),
        bgcolor=COLORS.SURFACE,
    )

def build_main_layout() -> ft.Column:
    header = build_header()
    input_section = build_input_section()
    terminal_section = build_terminal_section()
    control_panel = build_control_panel()
    
    content_row = ft.Row(
        controls=[input_section, terminal_section],
        spacing=16,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
    
    content_wrapper = ft.Container(content=content_row, padding=16)
    
    return ft.Column(
        controls=[
            header,
            ft.Container(content=content_wrapper, expand=True),
            control_panel,
        ],
        spacing=0,
        expand=True,
    )

def main(page: ft.Page) -> None:
    STATE.page = page
    page.title = f"{CONFIG.APP_NAME} - {CONFIG.APP_SUBTITLE}"
    page.bgcolor = COLORS.BACKGROUND
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    try:
        page.window_width = CONFIG.WINDOW_WIDTH
        page.window_height = CONFIG.WINDOW_HEIGHT
    except: pass
    
    page.add(build_main_layout())
    page.update()
    
    log_to_terminal("PRISMA iniciado correctamente", "success")
    log_to_terminal(f"Versión: {CONFIG.APP_VERSION}", "info")
    log_to_terminal("Modo Diagnóstico: FilePicker desactivado", "warning")

if __name__ == "__main__":
    ft.app(target=main)