"""
PRISMA - Application Layout (FIXED ARCHITECTURE)
=================================================
Corrected UI layout that solves:
1. FilePicker "Red Box" Error - FilePicker received via dependency injection
2. Layout Collapse (Gray Boxes) - Uses calculated dimensions, not excessive expand=True
3. Proper separation of concerns

Author: PRISMA Team
Version: 2.0.0
"""

import flet as ft
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, field

# Import theme from centralized location
from src.ui.theme import COLORS, TYPOGRAPHY, SPACING, CONFIG


# =============================================================================
# UI STATE MANAGEMENT
# =============================================================================

@dataclass
class UIState:
    """
    Centralized UI state container.
    Avoids global variables by using a single state object.
    """
    log_column: Optional[ft.Column] = None
    url_counter: Optional[ft.Text] = None
    execute_btn: Optional[ft.Container] = None
    ai_switch: Optional[ft.Switch] = None
    url_input: Optional[ft.TextField] = None
    report_btn: Optional[ft.Container] = None
    status_indicator: Optional[ft.Icon] = None
    status_text: Optional[ft.Text] = None
    progress_bar: Optional[ft.ProgressBar] = None
    progress_container: Optional[ft.Container] = None
    
    # Runtime state
    current_urls: list = field(default_factory=list)
    is_processing: bool = False


# =============================================================================
# COMPONENT FACTORY FUNCTIONS
# =============================================================================

def create_styled_button(
    text: str,
    icon: Optional[str] = None,
    variant: str = "primary",
    on_click: Optional[Callable] = None,
    disabled: bool = False,
    width: Optional[int] = None,
    height: int = 48,
) -> ft.Container:
    """
    Create a styled button with hover effects.
    
    Args:
        text: Button label
        icon: Optional Material icon name
        variant: "primary", "secondary", or "ghost"
        on_click: Click handler
        disabled: Whether button is disabled
        width: Optional fixed width (None = auto)
        height: Button height in pixels
    
    Returns:
        Styled Container acting as button
    """
    # Define colors based on variant
    colors_map = {
        "primary": {
            "bg": COLORS.PRIMARY,
            "hover": COLORS.PRIMARY_HOVER,
            "text": COLORS.TEXT_ON_PRIMARY,
        },
        "secondary": {
            "bg": COLORS.SURFACE,
            "hover": COLORS.SURFACE_HOVER,
            "text": COLORS.TEXT_PRIMARY,
        },
        "ghost": {
            "bg": "transparent",
            "hover": COLORS.SURFACE_HOVER,
            "text": COLORS.TEXT_SECONDARY,
        },
    }
    
    style = colors_map.get(variant, colors_map["primary"])
    
    bg_color = COLORS.SURFACE if disabled else style["bg"]
    text_color = COLORS.TEXT_MUTED if disabled else style["text"]
    
    # Build content row
    content_controls = []
    if icon:
        content_controls.append(
            ft.Icon(icon, size=18, color=text_color)
        )
    content_controls.append(
        ft.Text(
            text,
            size=TYPOGRAPHY.SIZE_BASE,
            weight=ft.FontWeight.W_500,
            color=text_color,
        )
    )
    
    button = ft.Container(
        content=ft.Row(
            controls=content_controls,
            spacing=SPACING.SM,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
        bgcolor=bg_color,
        border_radius=SPACING.RADIUS_MD,
        padding=ft.Padding(
            left=SPACING.LG,
            right=SPACING.LG,
            top=SPACING.SM + 4,
            bottom=SPACING.SM + 4,
        ),
        height=height,
        width=width,
        ink=not disabled,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
    )
    
    # Store metadata for hover/state management
    button.data = {
        "bg": style["bg"],
        "hover": style["hover"],
        "text": style["text"],
        "disabled": disabled,
        "variant": variant,
    }
    
    # Event handlers (only if not disabled)
    if not disabled:
        if on_click:
            button.on_click = on_click
        
        def handle_hover(e: ft.ControlEvent):
            if button.data.get("disabled"):
                return
            is_hovered = e.data == "true"
            button.bgcolor = button.data["hover"] if is_hovered else button.data["bg"]
            button.update()
        
        button.on_hover = handle_hover
    
    return button


def create_header(state: UIState) -> ft.Container:
    """Create the application header section."""
    
    logo_container = ft.Container(
        content=ft.Icon(
            "auto_awesome",
            size=28,
            color=COLORS.PRIMARY,
        ),
        bgcolor=COLORS.SURFACE,
        border_radius=SPACING.RADIUS_MD,
        padding=SPACING.SM,
        width=48,
        height=48,
    )
    
    title_column = ft.Column(
        controls=[
            ft.Text(
                CONFIG.APP_NAME,
                size=TYPOGRAPHY.SIZE_XL,
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
    
    return ft.Container(
        content=ft.Row(
            controls=[logo_container, title_column],
            spacing=SPACING.MD,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COLORS.BACKGROUND,
        padding=ft.Padding(
            left=SPACING.LG,
            right=SPACING.LG,
            top=SPACING.MD,
            bottom=SPACING.SM,
        ),
        height=72,
    )


def create_input_section(
    state: UIState,
    file_picker: ft.FilePicker,
    on_urls_changed: Optional[Callable] = None,
) -> ft.Container:
    """
    Create the input/drag-drop section.
    
    CRITICAL: file_picker is passed as parameter - it must already be in page.overlay.
    This function only REFERENCES it for triggering file selection.
    
    Args:
        state: UI state container
        file_picker: FilePicker instance (already in page.overlay)
        on_urls_changed: Callback when URLs are detected
    
    Returns:
        Input section container
    """
    
    # URL text input
    state.url_input = ft.TextField(
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
        border_radius=SPACING.RADIUS_MD,
        text_size=TYPOGRAPHY.SIZE_SM,
    )
    
    # Browse button - ONLY triggers file_picker, doesn't contain it
    def handle_browse_click(e: ft.ControlEvent):
        file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["txt", "docx"],
        )
    
    browse_button = create_styled_button(
        text="Seleccionar Archivos",
        icon="folder_open_rounded",
        variant="secondary",
        on_click=handle_browse_click,
    )
    
    # URL counter display
    state.url_counter = ft.Text(
        "0 enlaces detectados",
        size=TYPOGRAPHY.SIZE_SM,
        color=COLORS.TEXT_SECONDARY,
    )
    
    # Drag zone visual area
    drag_zone_content = ft.Column(
        controls=[
            ft.Icon(
                "upload_file_rounded",
                size=48,
                color=COLORS.TEXT_MUTED,
            ),
            ft.Text(
                "Arrastra archivos .txt o .docx aquí",
                color=COLORS.TEXT_SECONDARY,
                size=TYPOGRAPHY.SIZE_BASE,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=SPACING.SM),
            browse_button,
            ft.Container(height=SPACING.SM),
            ft.Text(
                "— o pega URLs directamente —",
                size=TYPOGRAPHY.SIZE_SM,
                color=COLORS.TEXT_MUTED,
            ),
            ft.Container(height=SPACING.XS),
            state.url_input,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=SPACING.XS,
    )
    
    drag_zone = ft.Container(
        content=drag_zone_content,
        bgcolor=COLORS.SURFACE,
        border=ft.border.all(2, COLORS.SURFACE_BORDER),
        border_radius=SPACING.RADIUS_LG,
        padding=SPACING.LG,
    )
    
    # Counter row
    counter_row = ft.Row(
        controls=[
            ft.Icon("link_rounded", size=16, color=COLORS.TEXT_SECONDARY),
            state.url_counter,
        ],
        spacing=SPACING.SM,
    )
    
    # Complete input section (NO FilePicker inside!)
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "ENTRADA",
                    size=TYPOGRAPHY.SIZE_XS,
                    weight=ft.FontWeight.W_600,
                    color=COLORS.TEXT_MUTED,
                ),
                drag_zone,
                counter_row,
            ],
            spacing=SPACING.SM,
        ),
        bgcolor=COLORS.BACKGROUND,
        padding=SPACING.MD,
        width=480,  # Fixed width prevents layout collapse
    )


def create_terminal_section(state: UIState) -> ft.Container:
    """
    Create the terminal/log section.
    
    Args:
        state: UI state container
    
    Returns:
        Terminal section container
    """
    
    # Log column with scrolling
    state.log_column = ft.Column(
        controls=[],
        spacing=2,
        scroll=ft.ScrollMode.AUTO,
        auto_scroll=True,
    )
    
    # Terminal container with fixed minimum height
    terminal_box = ft.Container(
        content=state.log_column,
        bgcolor=COLORS.TERMINAL_BG,
        border_radius=SPACING.RADIUS_MD,
        border=ft.border.all(1, COLORS.SURFACE_BORDER),
        padding=SPACING.MD,
        expand=True,
    )
    
    # Report button (hidden initially)
    state.report_btn = create_styled_button(
        text="Ver Reporte",
        icon="description_rounded",
        variant="secondary",
    )
    state.report_btn.visible = False
    state.report_btn.width = None  # Auto width
    
    # Terminal section container
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "TERMINAL",
                    size=TYPOGRAPHY.SIZE_XS,
                    weight=ft.FontWeight.W_600,
                    color=COLORS.TEXT_MUTED,
                ),
                terminal_box,
                state.report_btn,
            ],
            spacing=SPACING.SM,
            expand=True,
        ),
        bgcolor=COLORS.BACKGROUND,
        padding=SPACING.MD,
        expand=True,
    )


def create_control_panel(
    state: UIState,
    on_execute: Callable,
) -> ft.Container:
    """
    Create the bottom control panel with AI switch and execute button.
    
    Args:
        state: UI state container
        on_execute: Callback for execute button
    
    Returns:
        Control panel container
    """
    
    # AI Analysis switch
    state.ai_switch = ft.Switch(
        value=False,
        active_color=COLORS.PRIMARY,
        inactive_track_color=COLORS.SURFACE_BORDER,
    )
    
    ai_switch_row = ft.Row(
        controls=[
            state.ai_switch,
            ft.Text(
                "Análisis con IA",
                color=COLORS.TEXT_PRIMARY,
                size=TYPOGRAPHY.SIZE_BASE,
            ),
        ],
        spacing=SPACING.SM,
    )
    
    # Progress bar (hidden initially)
    state.progress_bar = ft.ProgressBar(
        value=0,
        color=COLORS.PRIMARY,
        bgcolor=COLORS.SURFACE_BORDER,
        height=4,
        border_radius=2,
    )
    
    state.progress_container = ft.Container(
        content=state.progress_bar,
        visible=False,
        padding=ft.Padding(top=SPACING.SM, bottom=0, left=0, right=0),
    )
    
    # Execute button
    state.execute_btn = create_styled_button(
        text="EJECUTAR INVESTIGACIÓN",
        icon="rocket_launch_rounded",
        variant="primary",
        on_click=lambda e: on_execute(),
        height=56,
    )
    
    # Make execute button expand to full width
    state.execute_btn.expand = True
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[ai_switch_row],
                    alignment=ft.MainAxisAlignment.START,
                ),
                state.progress_container,
                state.execute_btn,
            ],
            spacing=SPACING.MD,
        ),
        bgcolor=COLORS.SURFACE,
        padding=SPACING.LG,
        border=ft.Border(
            top=ft.BorderSide(1, COLORS.SURFACE_BORDER),
            bottom=ft.BorderSide(0, "transparent"),
            left=ft.BorderSide(0, "transparent"),
            right=ft.BorderSide(0, "transparent"),
        ),
        height=150,
    )


def create_status_bar(state: UIState) -> ft.Container:
    """
    Create the bottom status bar.
    
    Args:
        state: UI state container
    
    Returns:
        Status bar container
    """
    
    state.status_indicator = ft.Icon(
        "circle",
        size=8,
        color=COLORS.SUCCESS,
    )
    
    state.status_text = ft.Text(
        "Listo",
        size=TYPOGRAPHY.SIZE_SM,
        color=COLORS.TEXT_MUTED,
    )
    
    return ft.Container(
        content=ft.Row(
            controls=[
                state.status_indicator,
                state.status_text,
                ft.Container(expand=True),
                ft.Text(
                    f"{CONFIG.APP_NAME} v{CONFIG.APP_VERSION}",
                    size=TYPOGRAPHY.SIZE_XS,
                    color=COLORS.TEXT_MUTED,
                ),
            ],
            spacing=SPACING.SM,
        ),
        bgcolor=COLORS.BACKGROUND,
        padding=ft.Padding(
            left=SPACING.MD,
            right=SPACING.MD,
            top=SPACING.SM,
            bottom=SPACING.SM,
        ),
        border=ft.Border(
            top=ft.BorderSide(1, COLORS.SURFACE_BORDER),
            bottom=ft.BorderSide(0, "transparent"),
            left=ft.BorderSide(0, "transparent"),
            right=ft.BorderSide(0, "transparent"),
        ),
        height=36,
    )


# =============================================================================
# MAIN LAYOUT BUILDER
# =============================================================================

def build_app_ui(
    page: ft.Page,
    file_picker: ft.FilePicker,
    on_execute: Callable,
    state: Optional[UIState] = None,
) -> tuple[ft.Container, UIState]:
    """
    Build the complete application UI.
    
    CRITICAL ARCHITECTURE NOTES:
    1. file_picker MUST be added to page.overlay BEFORE calling this function
    2. file_picker is passed here only for REFERENCE (triggering file dialogs)
    3. file_picker is NEVER added to the visual tree inside this function
    
    Args:
        page: Flet Page instance
        file_picker: FilePicker instance (already in page.overlay!)
        on_execute: Callback for execute button
        state: Optional existing UIState (creates new if None)
    
    Returns:
        Tuple of (main_layout_container, ui_state)
    """
    
    # Create or use provided state
    ui_state = state or UIState()
    
    # Build all sections
    header = create_header(ui_state)
    input_section = create_input_section(ui_state, file_picker)
    terminal_section = create_terminal_section(ui_state)
    control_panel = create_control_panel(ui_state, on_execute)
    status_bar = create_status_bar(ui_state)
    
    # Main content area (Input + Terminal side by side)
    # Using Row with explicit vertical alignment to prevent collapse
    main_content = ft.Container(
        content=ft.Row(
            controls=[
                input_section,
                ft.VerticalDivider(
                    width=1,
                    color=COLORS.SURFACE_BORDER,
                ),
                terminal_section,
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True,
        ),
        expand=True,
        bgcolor=COLORS.BACKGROUND,
    )
    
    # Complete layout using Column
    # Key fix: Only the main_content gets expand=True
    # Header, control_panel, status_bar have fixed heights
    main_layout = ft.Container(
        content=ft.Column(
            controls=[
                header,
                ft.Divider(height=1, color=COLORS.SURFACE_BORDER),
                main_content,
                control_panel,
                status_bar,
            ],
            spacing=0,
            expand=True,
        ),
        bgcolor=COLORS.BACKGROUND,
        expand=True,
    )
    
    return main_layout, ui_state


# =============================================================================
# UI HELPER FUNCTIONS
# =============================================================================

def update_url_counter(state: UIState, count: int) -> None:
    """Update the URL counter display."""
    if state.url_counter:
        state.url_counter.value = f"{count} enlaces detectados"
        try:
            state.url_counter.update()
        except Exception:
            pass


def set_button_state(
    button: ft.Container,
    disabled: bool,
    text: Optional[str] = None,
) -> None:
    """
    Update button state (enabled/disabled) and optionally text.
    
    Args:
        button: Button container to update
        disabled: Whether button should be disabled
        text: Optional new text for button
    """
    if not button:
        return
    
    button.data["disabled"] = disabled
    
    if disabled:
        button.bgcolor = COLORS.SURFACE
        button.ink = False
    else:
        button.bgcolor = button.data.get("bg", COLORS.PRIMARY)
        button.ink = True
    
    # Update text if provided
    if text and isinstance(button.content, ft.Row):
        for control in button.content.controls:
            if isinstance(control, ft.Text):
                control.value = text
                control.color = COLORS.TEXT_MUTED if disabled else button.data.get("text", COLORS.TEXT_ON_PRIMARY)
    
    try:
        button.update()
    except Exception:
        pass


def set_status(
    state: UIState,
    message: str,
    status: str = "ready",
) -> None:
    """
    Update status bar message and indicator.
    
    Args:
        state: UI state container
        message: Status message to display
        status: Status type ("ready", "processing", "success", "error")
    """
    color_map = {
        "ready": COLORS.SUCCESS,
        "processing": COLORS.PRIMARY,
        "success": COLORS.SUCCESS,
        "error": COLORS.ERROR,
        "warning": COLORS.WARNING,
    }
    
    if state.status_indicator:
        state.status_indicator.color = color_map.get(status, COLORS.TEXT_MUTED)
        try:
            state.status_indicator.update()
        except Exception:
            pass
    
    if state.status_text:
        state.status_text.value = message
        try:
            state.status_text.update()
        except Exception:
            pass


def show_progress(state: UIState, visible: bool, value: float = 0) -> None:
    """
    Show or hide progress bar.
    
    Args:
        state: UI state container
        visible: Whether progress should be visible
        value: Progress value (0.0 to 1.0)
    """
    if state.progress_container:
        state.progress_container.visible = visible
        try:
            state.progress_container.update()
        except Exception:
            pass
    
    if state.progress_bar:
        state.progress_bar.value = value
        try:
            state.progress_bar.update()
        except Exception:
            pass