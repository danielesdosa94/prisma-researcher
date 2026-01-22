"""
PRISMA - UI Components (Safe Mode)
"""
from typing import Callable, Optional, List
from datetime import datetime
import flet as ft
from src.ui.theme import COLORS, TYPOGRAPHY, SPACING

class PrismaButton(ft.Container):
    def __init__(
        self,
        text: str,
        on_click: Optional[Callable] = None,
        icon: Optional[str] = None,
        disabled: bool = False,
        expand: bool = False,
        variant: str = "primary"
    ):
        # 1. Definir colores
        if variant == "primary":
            bg_color = COLORS.PRIMARY
            text_color = COLORS.TEXT_ON_PRIMARY
            hover_color = COLORS.PRIMARY_HOVER
        elif variant == "secondary":
            bg_color = COLORS.SURFACE
            text_color = COLORS.TEXT_PRIMARY
            hover_color = COLORS.SURFACE_HOVER
        else:
            bg_color = "transparent"
            text_color = COLORS.TEXT_SECONDARY
            hover_color = COLORS.SURFACE_HOVER

        # 2. Construir contenido visual
        content_controls = []
        if icon:
            content_controls.append(ft.Icon(icon, size=18, color=text_color))
        content_controls.append(
            ft.Text(text, size=14, weight=ft.FontWeight.W_500, color=text_color)
        )

        # 3. Inicializar Container SOLO con propiedades visuales
        super().__init__(
            content=ft.Row(
                controls=content_controls,
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            bgcolor=COLORS.SURFACE if disabled else bg_color,
            border_radius=SPACING.RADIUS_MD,
            padding=ft.padding.symmetric(horizontal=SPACING.LG, vertical=12),
            height=SPACING.BUTTON_HEIGHT,
            expand=expand,
            ink=not disabled,
        )

        # 4. Asignar evento DESPUÉS (Evita error 'unexpected keyword')
        if on_click and not disabled:
            self.on_click = on_click
            
        # Guardar colores para hover
        self._bg_color = bg_color
        self._hover_color = hover_color
        if not disabled:
            self.on_hover = self._handle_hover

    def _handle_hover(self, e):
        self.bgcolor = self._hover_color if e.data == "true" else self._bg_color
        self.update()

class PrismaTextField(ft.TextField):
    def __init__(
        self,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        on_change: Optional[Callable] = None,
        multiline: bool = False,
        password: bool = False,
        expand: bool = False,
    ):
        # Inicializar solo visuales
        super().__init__(
            label=label,
            hint_text=hint_text,
            multiline=multiline,
            password=password,
            expand=expand,
            min_lines=3 if multiline else 1,
            max_lines=10 if multiline else 1,
            height=SPACING.INPUT_HEIGHT if not multiline else None,
            border_color=COLORS.SURFACE_BORDER,
            focused_border_color=COLORS.PRIMARY,
            bgcolor=COLORS.SURFACE,
            color=COLORS.TEXT_PRIMARY,
            cursor_color=COLORS.PRIMARY,
            label_style=ft.TextStyle(color=COLORS.TEXT_SECONDARY),
            hint_style=ft.TextStyle(color=COLORS.TEXT_MUTED),
            border_radius=SPACING.RADIUS_MD,
        )
        # Asignar evento después
        if on_change:
            self.on_change = on_change

class PrismaSwitch(ft.Container):
    def __init__(self, label: str, value: bool = False, on_change: Optional[Callable] = None):
        # Crear switch sin evento
        self.switch = ft.Switch(
            value=value,
            active_color=COLORS.PRIMARY,
            inactive_track_color=COLORS.SURFACE_BORDER,
        )
        # Asignar evento después
        if on_change:
            self.switch.on_change = on_change
            
        super().__init__(
            content=ft.Row(
                controls=[
                    self.switch,
                    ft.Text(label, color=COLORS.TEXT_PRIMARY, size=TYPOGRAPHY.SIZE_BASE),
                ],
                spacing=SPACING.SM,
            ),
            padding=ft.padding.symmetric(vertical=SPACING.SM),
        )

    @property
    def value(self) -> bool:
        return self.switch.value

class TerminalLog(ft.Container):
    def __init__(self, height: int = 300):
        self.log_column = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO, auto_scroll=True)
        super().__init__(
            content=self.log_column,
            bgcolor=COLORS.TERMINAL_BG,
            border_radius=SPACING.RADIUS_MD,
            border=ft.border.all(1, COLORS.SURFACE_BORDER),
            padding=SPACING.MD,
            height=height,
            expand=True,
        )

    def add_log(self, message: str, status: str = "info", prefix: str = ">") -> None:
        color_map = {
            "info": COLORS.TEXT_SECONDARY, "success": COLORS.SUCCESS,
            "error": COLORS.ERROR, "warning": COLORS.WARNING, "ai": COLORS.PRIMARY
        }
        color = color_map.get(status, COLORS.TEXT_SECONDARY)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.log_column.controls.append(
            ft.Row([
                ft.Text(f"[{timestamp}]", color=COLORS.TEXT_MUTED, size=TYPOGRAPHY.SIZE_XS, font_family=TYPOGRAPHY.FONT_MONO),
                ft.Text(f"{prefix} {message}", color=color, size=TYPOGRAPHY.SIZE_SM, font_family=TYPOGRAPHY.FONT_MONO, selectable=True),
            ], spacing=SPACING.SM)
        )
        if len(self.log_column.controls) > 500:
            self.log_column.controls.pop(0)
        if self.page: self.update()

    def clear(self):
        self.log_column.controls.clear()
        if self.page: self.update()

class DragDropZone(ft.Container):
    def __init__(self, on_file_drop: Optional[Callable] = None, on_url_paste: Optional[Callable] = None):
        self.on_file_drop = on_file_drop
        
        # --- CORRECCIÓN CRÍTICA ---
        # 1. Crear FilePicker VACÍO (sin argumentos)
        self.file_picker = ft.FilePicker()
        # 2. Asignar evento después
        self.file_picker.on_result = self._handle_file_result
        
        self.url_input = ft.TextField(
            hint_text="Pega URLs aquí (una por línea)...",
            multiline=True,
            min_lines=3, max_lines=5,
            border_color=COLORS.SURFACE_BORDER,
            bgcolor=COLORS.SURFACE,
            color=COLORS.TEXT_PRIMARY,
            text_size=12,
        )
        
        # Botón
        self.browse_btn = PrismaButton(
            "Seleccionar Archivos", 
            icon="folder_open_rounded", 
            variant="secondary"
        )
        # Asignar click después para evitar problemas de inicialización
        self.browse_btn.on_click = lambda _: self.file_picker.pick_files(allow_multiple=True)

        super().__init__(
            content=ft.Column(
                controls=[
                    self.file_picker, # Añadir picker invisible al árbol visual
                    ft.Icon("upload_file_rounded", size=48, color=COLORS.TEXT_MUTED),
                    ft.Text("Arrastra archivos .txt o .docx aquí", color=COLORS.TEXT_SECONDARY),
                    ft.Container(height=10),
                    self.browse_btn,
                    ft.Container(height=10),
                    ft.Text("— o pega URLs directamente —", size=12, color=COLORS.TEXT_MUTED),
                    self.url_input,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=COLORS.SURFACE,
            border=ft.border.all(2, COLORS.SURFACE_BORDER),
            border_radius=SPACING.RADIUS_LG,
            padding=SPACING.LG,
            height=400,
        )

    def _handle_file_result(self, e: ft.ControlEvent): # Usar ControlEvent genérico
        if e.files and self.on_file_drop:
            self.on_file_drop([f.path for f in e.files])

    def get_urls(self) -> List[str]:
        return [line.strip() for line in (self.url_input.value or "").split("\n") if line.strip()]

    def clear(self):
        self.url_input.value = ""
        self.update()

class ProgressIndicator(ft.Container):
    def __init__(self, label: str = "Progreso"):
        self.progress_bar = ft.ProgressBar(value=0, color=COLORS.PRIMARY, bgcolor=COLORS.SURFACE_BORDER)
        self.label = ft.Text(label, size=12, color=COLORS.TEXT_SECONDARY)
        super().__init__(
            content=ft.Column([self.label, self.progress_bar]),
            visible=False
        )
    
    def set_progress(self, value: float, label: str = None):
        self.progress_bar.value = value
        if label: self.label.value = label
        self.update()
        
    def show(self): self.visible = True; self.update()
    def hide(self): self.visible = False; self.update()

class StatusBar(ft.Container):
    def __init__(self):
        self.status = ft.Text("Listo", size=12, color=COLORS.TEXT_MUTED)
        super().__init__(
            content=ft.Row([ft.Icon("circle", size=8, color=COLORS.SUCCESS), self.status]),
            bgcolor=COLORS.BACKGROUND,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border=ft.border.only(top=ft.BorderSide(1, COLORS.SURFACE_BORDER))
        )
    def set_status(self, msg, status="idle"):
        self.status.value = msg
        self.update()