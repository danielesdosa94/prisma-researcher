"""
PRISMA - Main Layout
====================
Main window structure and layout composition.
Implements the two-column layout with input zone, terminal, and controls.
"""

from typing import Callable, Optional, List
import flet as ft

from src.ui.theme import COLORS, TYPOGRAPHY, SPACING, CONFIG
from src.ui.components import (
    PrismaButton,
    PrismaSwitch,
    TerminalLog,
    DragDropZone,
    ProgressIndicator,
    StatusBar,
)


class HeaderSection(ft.Container):
    """
    Top header with app branding and title.
    """
    
    def __init__(self):
        # Logo/Icon
        logo = ft.Container(
            content=ft.Icon(
                "auto_awesome",
                size=32,
                color=COLORS.PRIMARY,
            ),
            bgcolor=COLORS.SURFACE,
            border_radius=SPACING.RADIUS_MD,
            padding=SPACING.SM,
        )
        
        # Title
        title = ft.Column(
            controls=[
                ft.Text(
                    CONFIG.APP_NAME,
                    size=TYPOGRAPHY.SIZE_2XL,
                    weight=ft.FontWeight.W_700,
                    color=COLORS.TEXT_PRIMARY,
                ),
                ft.Text(
                    CONFIG.APP_SUBTITLE,
                    size=TYPOGRAPHY.SIZE_SM,
                    color=COLORS.TEXT_SECONDARY,
                ),
            ],
            spacing=0,
        )
        
        super().__init__(
            content=ft.Row(
                controls=[logo, title],
                spacing=SPACING.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(
                left=SPACING.LG,
                right=SPACING.LG,
                top=SPACING.MD,
                bottom=SPACING.SM,
            ),
        )


class InputSection(ft.Container):
    """
    Left panel containing the drag-drop zone and URL input.
    """
    
    def __init__(
        self,
        on_file_drop: Optional[Callable] = None,
    ):
        self.drag_drop_zone = DragDropZone(on_file_drop=on_file_drop)
        
        # Detected items counter
        self.items_counter = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        "link_rounded",
                        size=16,
                        color=COLORS.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        "0 enlaces detectados",
                        size=TYPOGRAPHY.SIZE_SM,
                        color=COLORS.TEXT_SECONDARY,
                    ),
                ],
                spacing=SPACING.XS,
            ),
            padding=ft.padding.symmetric(vertical=SPACING.SM),
        )
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "ENTRADA",
                        size=TYPOGRAPHY.SIZE_XS,
                        weight=ft.FontWeight.W_600,
                        color=COLORS.TEXT_MUTED,
                    ),
                    self.drag_drop_zone,
                    self.items_counter,
                ],
                spacing=SPACING.SM,
                expand=True,
            ),
            bgcolor=COLORS.BACKGROUND,
            padding=SPACING.MD,
            expand=True,
        )
    
    def update_counter(self, count: int) -> None:
        """Update the detected items counter."""
        text = f"{count} enlace{'s' if count != 1 else ''} detectado{'s' if count != 1 else ''}"
        self.items_counter.content.controls[1].value = text
        self.items_counter.update()
    
    def get_urls(self) -> List[str]:
        """Get URLs from the drag-drop zone."""
        return self.drag_drop_zone.get_urls()
    
    def clear(self) -> None:
        """Clear all inputs."""
        self.drag_drop_zone.clear()
        self.update_counter(0)


class TerminalSection(ft.Container):
    """
    Right panel containing the live log terminal.
    """
    
    def __init__(self):
        self.terminal = TerminalLog(height=350)

        # View report button (hidden initially)
        self.view_report_btn = PrismaButton(
            text="Ver Reporte Final",
            icon="description_rounded",
            variant="primary",
            expand=True,
        )
        self.view_report_btn.visible = False
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "TERMINAL",
                        size=TYPOGRAPHY.SIZE_XS,
                        weight=ft.FontWeight.W_600,
                        color=COLORS.TEXT_MUTED,
                    ),
                    self.terminal,
                    self.view_report_btn,
                ],
                spacing=SPACING.SM,
                expand=True,
            ),
            bgcolor=COLORS.BACKGROUND,
            padding=SPACING.MD,
            expand=True,
        )
    
    def log(self, message: str, status: str = "info") -> None:
        """Add log entry to terminal."""
        self.terminal.add_log(message, status)
    
    def clear(self) -> None:
        """Clear terminal."""
        self.terminal.clear()
    
    def show_report_button(self, on_click: Callable) -> None:
        """Show the view report button."""
        self.view_report_btn.on_click = on_click
        self.view_report_btn.visible = True
        self.view_report_btn.update()
    
    def hide_report_button(self) -> None:
        """Hide the view report button."""
        self.view_report_btn.visible = False
        self.view_report_btn.update()


class ControlPanel(ft.Container):
    """
    Bottom control panel with mode selection and execute button.
    """
    
    def __init__(
        self,
        on_execute: Optional[Callable] = None,
        on_mode_change: Optional[Callable] = None,
    ):
        self.on_execute = on_execute
        self.on_mode_change = on_mode_change

        # Mode switches - create without on_change
        self.ai_switch = PrismaSwitch(
            label="Análisis con IA",
            value=False,
        )
        # Set handler after initialization
        self.ai_switch.switch.on_change = self._handle_mode_change
        
        # AI status indicator
        self.ai_status = ft.Row(
            controls=[
                ft.Icon(
                    "memory_rounded",
                    size=16,
                    color=COLORS.TEXT_MUTED,
                ),
                ft.Text(
                    "IA no descargada",
                    size=TYPOGRAPHY.SIZE_XS,
                    color=COLORS.TEXT_MUTED,
                ),
            ],
            spacing=SPACING.XS,
        )
        
        # Progress indicator for model download
        self.progress = ProgressIndicator(label="Descargando modelo...")

        # Execute button - create without on_click
        self.execute_btn = PrismaButton(
            text="EJECUTAR INVESTIGACIÓN",
            icon="rocket_launch_rounded",
            variant="primary",
            expand=True,
        )
        # Set handler after initialization
        self.execute_btn.on_click = self._handle_execute
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "MODO DE OPERACIÓN",
                                            size=TYPOGRAPHY.SIZE_XS,
                                            weight=ft.FontWeight.W_600,
                                            color=COLORS.TEXT_MUTED,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Radio(
                                                    value="scrape",
                                                    label="Solo Scraping (.md)",
                                                    fill_color={
                                                        ft.ControlState.SELECTED: COLORS.PRIMARY,
                                                    },
                                                ),
                                                ft.Radio(
                                                    value="analyze",
                                                    label="Scraping + Análisis IA",
                                                    fill_color={
                                                        ft.ControlState.SELECTED: COLORS.PRIMARY,
                                                    },
                                                ),
                                            ],
                                        ),
                                    ],
                                    spacing=SPACING.XS,
                                ),
                                ft.Container(expand=True),
                                ft.Column(
                                    controls=[
                                        self.ai_status,
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                            ],
                        ),
                        padding=ft.padding.only(bottom=SPACING.SM),
                    ),
                    self.progress,
                    self.execute_btn,
                ],
                spacing=SPACING.MD,
            ),
            bgcolor=COLORS.SURFACE,
            border_radius=SPACING.RADIUS_LG,
            border=ft.border.all(1, COLORS.SURFACE_BORDER),
            padding=SPACING.LG,
            margin=ft.margin.symmetric(horizontal=SPACING.MD),
        )
        
        # Radio group - create without on_change
        self.mode_group = ft.RadioGroup(
            value="scrape",
            content=self.content.controls[0].content.controls[0].controls[1],
        )
        # Set handler after initialization
        self.mode_group.on_change = self._handle_mode_change
    
    def _handle_mode_change(self, e: ft.ControlEvent) -> None:
        """Handle mode selection change."""
        if self.on_mode_change:
            self.on_mode_change(e.control.value if hasattr(e.control, 'value') else "scrape")
    
    def _handle_execute(self, _e: ft.ControlEvent) -> None:
        """Handle execute button click."""
        if self.on_execute:
            self.on_execute()
    
    def get_mode(self) -> str:
        """Get current operation mode."""
        return self.mode_group.value or "scrape"
    
    def set_ai_status(self, status: str, available: bool = False) -> None:
        """
        Update AI status display.
        
        Args:
            status: Status message
            available: Whether AI is ready to use
        """
        color = COLORS.SUCCESS if available else COLORS.TEXT_MUTED
        icon = "check_circle_rounded" if available else "memory_rounded"

        self.ai_status.controls[0].name = icon
        self.ai_status.controls[0].color = color
        self.ai_status.controls[1].value = status
        self.ai_status.controls[1].color = color
        self.ai_status.update()
    
    def set_executing(self, executing: bool) -> None:
        """Toggle button state during execution."""
        self.execute_btn.disabled = executing
        self.execute_btn.text = "PROCESANDO..." if executing else "EJECUTAR INVESTIGACIÓN"
        self.execute_btn.icon = "hourglass_top_rounded" if executing else "rocket_launch_rounded"
        self.execute_btn.update()
    
    def show_progress(self, value: float, label: str = "Descargando modelo...") -> None:
        """Show and update progress bar."""
        self.progress.set_progress(value, label)
        self.progress.show()
    
    def hide_progress(self) -> None:
        """Hide progress bar."""
        self.progress.hide()


class MainLayout(ft.Container):
    """
    Main application layout composing all sections.
    """
    
    def __init__(
        self,
        on_execute: Optional[Callable] = None,
        on_mode_change: Optional[Callable] = None,
        on_file_drop: Optional[Callable] = None,
    ):
        # Create sections
        self.header = HeaderSection()
        self.input_section = InputSection(on_file_drop=on_file_drop)
        self.terminal_section = TerminalSection()
        self.control_panel = ControlPanel(
            on_execute=on_execute,
            on_mode_change=on_mode_change,
        )
        self.status_bar = StatusBar()
        
        # Main content area (two columns)
        main_content = ft.Row(
            controls=[
                self.input_section,
                ft.VerticalDivider(width=1, color=COLORS.SURFACE_BORDER),
                self.terminal_section,
            ],
            expand=True,
            spacing=0,
        )
        
        super().__init__(
            content=ft.Column(
                controls=[
                    self.header,
                    ft.Divider(height=1, color=COLORS.SURFACE_BORDER),
                    main_content,
                    self.control_panel,
                    ft.Container(height=SPACING.SM),
                    self.status_bar,
                ],
                spacing=0,
                expand=True,
            ),
            bgcolor=COLORS.BACKGROUND,
            expand=True,
        )
    
    # Convenience methods to access child components
    def log(self, message: str, status: str = "info") -> None:
        """Add log to terminal."""
        self.terminal_section.log(message, status)
    
    def clear_terminal(self) -> None:
        """Clear terminal logs."""
        self.terminal_section.clear()
    
    def set_status(self, message: str, status: str = "idle") -> None:
        """Update status bar."""
        self.status_bar.set_status(message, status)
    
    def get_urls(self) -> List[str]:
        """Get URLs from input section."""
        return self.input_section.get_urls()
    
    def update_url_counter(self, count: int) -> None:
        """Update URL counter."""
        self.input_section.update_counter(count)
    
    def get_mode(self) -> str:
        """Get operation mode."""
        return self.control_panel.get_mode()
    
    def set_executing(self, executing: bool) -> None:
        """Set execution state."""
        self.control_panel.set_executing(executing)
        status = "Procesando..." if executing else "Esperando órdenes..."
        self.set_status(status, "working" if executing else "idle")
