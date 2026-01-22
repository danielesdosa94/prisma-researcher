"""
PRISMA - Main Layout (Safe Mode)
"""
from typing import Callable, Optional, List
import flet as ft
from src.ui.theme import COLORS, TYPOGRAPHY, SPACING, CONFIG
from src.ui.components import PrismaButton, PrismaSwitch, TerminalLog, DragDropZone, ProgressIndicator, StatusBar

class HeaderSection(ft.Container):
    def __init__(self):
        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon("auto_awesome", size=32, color=COLORS.PRIMARY),
                        bgcolor=COLORS.SURFACE, border_radius=SPACING.RADIUS_MD, padding=SPACING.SM
                    ),
                    ft.Column([
                        ft.Text(CONFIG.APP_NAME, size=24, weight=ft.FontWeight.W_700, color=COLORS.TEXT_PRIMARY),
                        ft.Text(CONFIG.APP_SUBTITLE, size=12, color=COLORS.TEXT_SECONDARY),
                    ], spacing=0)
                ],
                spacing=SPACING.MD,
            ),
            bgcolor=COLORS.BACKGROUND,
            padding=ft.padding.only(left=24, right=24, top=16, bottom=8)
        )

class InputSection(ft.Container):
    def __init__(self, on_file_drop: Optional[Callable] = None):
        self.drag_drop_zone = DragDropZone(on_file_drop=on_file_drop)
        self.counter_text = ft.Text("0 enlaces detectados", size=12, color=COLORS.TEXT_SECONDARY)
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("ENTRADA", size=11, weight=ft.FontWeight.W_600, color=COLORS.TEXT_MUTED),
                    self.drag_drop_zone,
                    ft.Row([ft.Icon("link_rounded", size=16, color=COLORS.TEXT_SECONDARY), self.counter_text]),
                ],
                spacing=10,
                expand=True
            ),
            bgcolor=COLORS.BACKGROUND,
            padding=16,
            expand=True
        )

    def update_counter(self, count):
        self.counter_text.value = f"{count} enlaces detectados"
        self.counter_text.update()
    
    def get_urls(self): return self.drag_drop_zone.get_urls()

class TerminalSection(ft.Container):
    def __init__(self):
        self.terminal = TerminalLog(height=None)
        # Botón inicial sin evento
        self.report_btn = PrismaButton("Ver Reporte", icon="description_rounded", expand=True)
        self.report_btn.visible = False
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("TERMINAL", size=11, weight=ft.FontWeight.W_600, color=COLORS.TEXT_MUTED),
                    self.terminal,
                    self.report_btn
                ],
                spacing=10,
                expand=True
            ),
            bgcolor=COLORS.BACKGROUND,
            padding=16,
            expand=True
        )

    def log(self, msg, status="info"): self.terminal.add_log(msg, status)
    def clear(self): self.terminal.clear()
    def show_report_button(self, on_click): 
        self.report_btn.on_click = on_click
        self.report_btn.visible = True
        self.report_btn.update()

class ControlPanel(ft.Container):
    def __init__(self, on_execute=None, on_mode_change=None):
        # Manejador seguro para switch
        def handle_switch_change(e):
            if on_mode_change:
                val = "analyze" if e.control.value else "scrape"
                on_mode_change(val)

        self.ai_switch = PrismaSwitch("Análisis con IA", on_change=handle_switch_change)
        self.progress = ProgressIndicator()
        
        # Manejador seguro para botón execute
        def handle_execute_click(_):
            if on_execute:
                on_execute()

        self.execute_btn = PrismaButton("EJECUTAR INVESTIGACIÓN", icon="rocket_launch_rounded", expand=True)
        self.execute_btn.on_click = handle_execute_click # Asignación tardía
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Row([self.ai_switch], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    self.progress,
                    self.execute_btn
                ],
                spacing=16
            ),
            bgcolor=COLORS.SURFACE,
            padding=24,
            border=ft.border.only(top=ft.BorderSide(1, COLORS.SURFACE_BORDER))
        )
        
    def get_mode(self): return "analyze" if self.ai_switch.value else "scrape"
    def set_executing(self, active):
        self.execute_btn.disabled = active
        self.execute_btn.text = "PROCESANDO..." if active else "EJECUTAR INVESTIGACIÓN"
        self.execute_btn.update()
    def set_ai_status(self, msg, available): pass 
    def show_progress(self, val, label): self.progress.set_progress(val, label); self.progress.show()
    def hide_progress(self): self.progress.hide()

class MainLayout(ft.Container):
    def __init__(self, on_execute=None, on_mode_change=None, on_file_drop=None):
        self.input_section = InputSection(on_file_drop)
        self.terminal_section = TerminalSection()
        self.control_panel = ControlPanel(on_execute, on_mode_change)
        self.status_bar = StatusBar()
        
        super().__init__(
            content=ft.Column(
                controls=[
                    HeaderSection(),
                    ft.Divider(height=1, color=COLORS.SURFACE_BORDER),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.input_section,
                                ft.VerticalDivider(width=1, color=COLORS.SURFACE_BORDER),
                                self.terminal_section
                            ],
                            spacing=0,
                            expand=True
                        ),
                        expand=True 
                    ),
                    self.control_panel,
                    self.status_bar
                ],
                spacing=0,
                expand=True
            ),
            bgcolor=COLORS.BACKGROUND,
            expand=True
        )

    # Proxy methods
    def log(self, *args): self.terminal_section.log(*args)
    def get_urls(self): return self.input_section.get_urls()
    def update_url_counter(self, c): self.input_section.update_counter(c)
    def get_mode(self): return self.control_panel.get_mode()
    def set_executing(self, e): self.control_panel.set_executing(e); self.status_bar.set_status("Procesando..." if e else "Listo")
    def set_status(self, m, s): self.status_bar.set_status(m, s)