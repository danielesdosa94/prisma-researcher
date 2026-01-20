"""
PRISMA - UI Components
======================
Reusable UI components following the PRISMA design system.
All components use the centralized theme configuration.
"""

from typing import Callable, Optional, List
from datetime import datetime
import flet as ft

from src.ui.theme import COLORS, TYPOGRAPHY, SPACING


class PrismaButton(ft.ElevatedButton):
    """
    Primary action button with PRISMA styling.
    
    Args:
        text: Button label
        on_click: Click handler callback
        icon: Optional icon (ft.icons.XXXX)
        disabled: Whether button is disabled
        expand: Whether to expand to fill container
        variant: 'primary' | 'secondary' | 'ghost'
    """
    
    def __init__(
        self,
        text: str,
        on_click: Optional[Callable] = None,
        icon: Optional[str] = None,
        disabled: bool = False,
        expand: bool = False,
        variant: str = "primary"
    ):
        # Determine colors based on variant
        if variant == "primary":
            bg_color = COLORS.PRIMARY
            text_color = COLORS.TEXT_ON_PRIMARY
        elif variant == "secondary":
            bg_color = COLORS.SURFACE
            text_color = COLORS.TEXT_PRIMARY
        else:  # ghost
            bg_color = "transparent"
            text_color = COLORS.TEXT_SECONDARY
        
        super().__init__(
            text=text,
            icon=icon,
            on_click=on_click,
            disabled=disabled,
            expand=expand,
            height=SPACING.BUTTON_HEIGHT,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: bg_color,
                    ft.ControlState.HOVERED: COLORS.PRIMARY_HOVER if variant == "primary" else COLORS.SURFACE_HOVER,
                    ft.ControlState.DISABLED: COLORS.SURFACE,
                },
                color={
                    ft.ControlState.DEFAULT: text_color,
                    ft.ControlState.DISABLED: COLORS.TEXT_MUTED,
                },
                shape=ft.RoundedRectangleBorder(radius=SPACING.RADIUS_MD),
                padding=ft.padding.symmetric(horizontal=SPACING.LG),
            ),
        )


class PrismaTextField(ft.TextField):
    """
    Styled text input field for PRISMA.
    
    Args:
        label: Field label
        hint_text: Placeholder text
        on_change: Change handler
        multiline: Enable multiline input
        password: Mask input as password
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        on_change: Optional[Callable] = None,
        multiline: bool = False,
        password: bool = False,
        expand: bool = False,
    ):
        super().__init__(
            label=label,
            hint_text=hint_text,
            on_change=on_change,
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


class PrismaSwitch(ft.Container):
    """
    Toggle switch with label for PRISMA.
    
    Args:
        label: Switch label
        value: Initial state
        on_change: Change handler
    """
    
    def __init__(
        self,
        label: str,
        value: bool = False,
        on_change: Optional[Callable] = None,
    ):
        self.switch = ft.Switch(
            value=value,
            active_color=COLORS.PRIMARY,
            inactive_track_color=COLORS.SURFACE_BORDER,
            on_change=on_change,
        )
        
        super().__init__(
            content=ft.Row(
                controls=[
                    self.switch,
                    ft.Text(
                        label,
                        color=COLORS.TEXT_PRIMARY,
                        size=TYPOGRAPHY.SIZE_BASE,
                    ),
                ],
                spacing=SPACING.SM,
            ),
            padding=ft.padding.symmetric(vertical=SPACING.SM),
        )
    
    @property
    def value(self) -> bool:
        return self.switch.value
    
    @value.setter
    def value(self, val: bool):
        self.switch.value = val


class TerminalLog(ft.Container):
    """
    Terminal-style log display component.
    Shows real-time logs with timestamp and status colors.
    """
    
    def __init__(self, height: int = 300):
        self.log_entries: List[ft.Control] = []
        self.log_column = ft.Column(
            controls=[],
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            auto_scroll=True,
        )
        
        super().__init__(
            content=self.log_column,
            bgcolor=COLORS.TERMINAL_BG,
            border_radius=SPACING.RADIUS_MD,
            border=ft.border.all(1, COLORS.SURFACE_BORDER),
            padding=SPACING.MD,
            height=height,
            expand=True,
        )
    
    def add_log(
        self,
        message: str,
        status: str = "info",
        prefix: str = ">"
    ) -> None:
        """
        Add a log entry to the terminal.
        
        Args:
            message: Log message
            status: 'info' | 'success' | 'error' | 'warning' | 'ai'
            prefix: Line prefix character
        """
        # Determine color based on status
        color_map = {
            "info": COLORS.TEXT_SECONDARY,
            "success": COLORS.SUCCESS,
            "error": COLORS.ERROR,
            "warning": COLORS.WARNING,
            "ai": COLORS.PRIMARY,
        }
        color = color_map.get(status, COLORS.TEXT_SECONDARY)
        
        # Create timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create log entry
        entry = ft.Row(
            controls=[
                ft.Text(
                    f"[{timestamp}]",
                    color=COLORS.TEXT_MUTED,
                    size=TYPOGRAPHY.SIZE_XS,
                    font_family=TYPOGRAPHY.FONT_MONO,
                ),
                ft.Text(
                    f"{prefix} {message}",
                    color=color,
                    size=TYPOGRAPHY.SIZE_SM,
                    font_family=TYPOGRAPHY.FONT_MONO,
                    selectable=True,
                ),
            ],
            spacing=SPACING.SM,
        )
        
        self.log_entries.append(entry)
        self.log_column.controls.append(entry)
        
        # Keep only last 500 entries to prevent memory issues
        if len(self.log_entries) > 500:
            removed = self.log_entries.pop(0)
            self.log_column.controls.remove(removed)
        
        self.update()
    
    def clear(self) -> None:
        """Clear all log entries."""
        self.log_entries.clear()
        self.log_column.controls.clear()
        self.update()


class DragDropZone(ft.Container):
    """
    File drag-and-drop zone with visual feedback.
    Accepts .txt, .docx files or URLs.
    """
    
    def __init__(
        self,
        on_file_drop: Optional[Callable] = None,
        on_url_paste: Optional[Callable] = None,
    ):
        self.on_file_drop = on_file_drop
        self.on_url_paste = on_url_paste
        self.is_dragging = False
        
        # URL input field
        self.url_input = ft.TextField(
            hint_text="Pega URLs aquí (una por línea)...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_color=COLORS.SURFACE_BORDER,
            focused_border_color=COLORS.PRIMARY,
            bgcolor=COLORS.SURFACE,
            color=COLORS.TEXT_PRIMARY,
            cursor_color=COLORS.PRIMARY,
            hint_style=ft.TextStyle(color=COLORS.TEXT_MUTED),
            border_radius=SPACING.RADIUS_SM,
            on_change=self._handle_url_change,
        )
        
        # File picker
        self.file_picker = ft.FilePicker(
            on_result=self._handle_file_result,
        )
        
        # Main content
        self.drop_icon = ft.Icon(
            "upload_file_rounded",
            size=48,
            color=COLORS.TEXT_MUTED,
        )
        
        self.drop_text = ft.Text(
            "Arrastra archivos .txt o .docx aquí",
            size=TYPOGRAPHY.SIZE_BASE,
            color=COLORS.TEXT_SECONDARY,
            text_align=ft.TextAlign.CENTER,
        )
        
        self.browse_button = PrismaButton(
            text="Seleccionar Archivos",
            icon="folder_open_rounded",
            variant="secondary",
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=["txt", "docx"]
            ),
        )
        
        super().__init__(
            content=ft.Column(
                controls=[
                    self.file_picker,
                    self.drop_icon,
                    self.drop_text,
                    ft.Container(height=SPACING.SM),
                    self.browse_button,
                    ft.Container(height=SPACING.MD),
                    ft.Text(
                        "— o pega URLs directamente —",
                        size=TYPOGRAPHY.SIZE_SM,
                        color=COLORS.TEXT_MUTED,
                    ),
                    ft.Container(height=SPACING.SM),
                    self.url_input,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=SPACING.XS,
            ),
            bgcolor=COLORS.SURFACE,
            border=ft.border.all(2, COLORS.SURFACE_BORDER),
            border_radius=SPACING.RADIUS_LG,
            padding=SPACING.LG,
            expand=True,
            on_hover=self._handle_hover,
        )
    
    def _handle_hover(self, e: ft.HoverEvent) -> None:
        """Handle hover state for visual feedback."""
        if e.data == "true":
            self.border = ft.border.all(2, COLORS.PRIMARY)
            self.bgcolor = COLORS.DRAG_ZONE_ACTIVE
        else:
            self.border = ft.border.all(2, COLORS.SURFACE_BORDER)
            self.bgcolor = COLORS.SURFACE
        self.update()
    
    def _handle_file_result(self, e: ft.ControlEvent) -> None:
        """Handle file picker result."""
        if e.files and self.on_file_drop:
            file_paths = [f.path for f in e.files]
            self.on_file_drop(file_paths)
    
    def _handle_url_change(self, e: ft.ControlEvent) -> None:
        """Handle URL input changes."""
        pass  # URL processing happens on execute
    
    def get_urls(self) -> List[str]:
        """Extract URLs from the input field."""
        text = self.url_input.value or ""
        lines = text.strip().split("\n")
        urls = [line.strip() for line in lines if line.strip()]
        return urls
    
    def clear(self) -> None:
        """Clear the URL input."""
        self.url_input.value = ""
        self.update()


class ProgressIndicator(ft.Container):
    """
    Progress bar with label and percentage.
    """
    
    def __init__(self, label: str = "Progreso"):
        self.label_text = ft.Text(
            label,
            color=COLORS.TEXT_SECONDARY,
            size=TYPOGRAPHY.SIZE_SM,
        )
        
        self.percentage_text = ft.Text(
            "0%",
            color=COLORS.TEXT_PRIMARY,
            size=TYPOGRAPHY.SIZE_SM,
            weight=ft.FontWeight.W_600,
        )
        
        self.progress_bar = ft.ProgressBar(
            value=0,
            bgcolor=COLORS.SURFACE_BORDER,
            color=COLORS.PRIMARY,
            height=8,
            border_radius=4,
        )
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.label_text,
                            self.percentage_text,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.progress_bar,
                ],
                spacing=SPACING.XS,
            ),
            visible=False,
        )
    
    def set_progress(self, value: float, label: Optional[str] = None) -> None:
        """
        Update progress value (0.0 to 1.0).
        """
        self.progress_bar.value = max(0, min(1, value))
        self.percentage_text.value = f"{int(value * 100)}%"
        if label:
            self.label_text.value = label
        self.update()
    
    def show(self) -> None:
        """Show the progress indicator."""
        self.visible = True
        self.update()
    
    def hide(self) -> None:
        """Hide the progress indicator."""
        self.visible = False
        self.progress_bar.value = 0
        self.percentage_text.value = "0%"
        self.update()


class StatusBar(ft.Container):
    """
    Bottom status bar showing app state.
    """
    
    def __init__(self):
        self.status_text = ft.Text(
            "Esperando órdenes...",
            color=COLORS.TEXT_MUTED,
            size=TYPOGRAPHY.SIZE_SM,
            font_family=TYPOGRAPHY.FONT_MONO,
        )
        
        self.version_text = ft.Text(
            "v1.0 Local Build",
            color=COLORS.TEXT_MUTED,
            size=TYPOGRAPHY.SIZE_XS,
        )
        
        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                "circle",
                                size=8,
                                color=COLORS.SUCCESS,
                            ),
                            self.status_text,
                        ],
                        spacing=SPACING.SM,
                    ),
                    self.version_text,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLORS.BACKGROUND,
            border=ft.border.only(top=ft.BorderSide(1, COLORS.SURFACE_BORDER)),
            padding=ft.padding.symmetric(horizontal=SPACING.MD, vertical=SPACING.SM),
        )
    
    def set_status(self, message: str, status: str = "idle") -> None:
        """
        Update status message.
        
        Args:
            message: Status message
            status: 'idle' | 'working' | 'success' | 'error'
        """
        color_map = {
            "idle": COLORS.TEXT_MUTED,
            "working": COLORS.PRIMARY,
            "success": COLORS.SUCCESS,
            "error": COLORS.ERROR,
        }
        
        icon_map = {
            "idle": COLORS.SUCCESS,
            "working": COLORS.PRIMARY,
            "success": COLORS.SUCCESS,
            "error": COLORS.ERROR,
        }
        
        self.status_text.value = message
        self.status_text.color = color_map.get(status, COLORS.TEXT_MUTED)
        self.update()
