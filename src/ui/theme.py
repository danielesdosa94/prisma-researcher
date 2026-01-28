"""
PRISMA - Theme Configuration
============================
Centralized design system with colors, typography, and spacing.
All UI components should import from this module.
"""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Colors:
    """PRISMA color palette - Dark/Violet aesthetic."""
    
    # Backgrounds
    BACKGROUND: Final[str] = "#0F1115"      # Charcoal Deep
    SURFACE: Final[str] = "#1E2129"         # Gunmetal
    SURFACE_HOVER: Final[str] = "#282D38"   # Slightly lighter for hover
    SURFACE_BORDER: Final[str] = "#2D333D"  # Subtle borders
    
    # Accents
    PRIMARY: Final[str] = "#8B5CF6"         # Electric Violet
    PRIMARY_HOVER: Final[str] = "#A78BFA"   # Lighter violet
    PRIMARY_DIM: Final[str] = "#6D28D9"     # Darker violet
    SUCCESS: Final[str] = "#10B981"         # Emerald Green
    ERROR: Final[str] = "#EF4444"           # Red
    WARNING: Final[str] = "#F59E0B"         # Amber
    
    # Text
    TEXT_PRIMARY: Final[str] = "#F1F5F9"    # Off-white
    TEXT_SECONDARY: Final[str] = "#94A3B8"  # Slate (logs/code)
    TEXT_MUTED: Final[str] = "#64748B"      # Muted text
    TEXT_ON_PRIMARY: Final[str] = "#FFFFFF" # White on violet
    
    # Special
    TERMINAL_BG: Final[str] = "#0A0C0F"     # Darker for terminal
    DRAG_ZONE_ACTIVE: Final[str] = "#8B5CF620"  # Violet with opacity


@dataclass(frozen=True)
class Typography:
    """Font configuration for PRISMA."""
    
    # Font families
    FONT_UI: Final[str] = "Inter"
    FONT_MONO: Final[str] = "JetBrains Mono"
    
    # Font sizes
    SIZE_XS: Final[int] = 11
    SIZE_SM: Final[int] = 13
    SIZE_BASE: Final[int] = 14
    SIZE_LG: Final[int] = 16
    SIZE_XL: Final[int] = 20
    SIZE_2XL: Final[int] = 24
    SIZE_3XL: Final[int] = 32
    
    # Font weights
    WEIGHT_NORMAL: Final[str] = "w400"
    WEIGHT_MEDIUM: Final[str] = "w500"
    WEIGHT_SEMIBOLD: Final[str] = "w600"
    WEIGHT_BOLD: Final[str] = "w700"


@dataclass(frozen=True)
class Spacing:
    """Spacing and sizing constants."""
    
    # Padding/Margin
    XS: Final[int] = 4
    SM: Final[int] = 8
    MD: Final[int] = 16
    LG: Final[int] = 24
    XL: Final[int] = 32
    XXL: Final[int] = 48
    
    # Border radius
    RADIUS_SM: Final[int] = 4
    RADIUS_MD: Final[int] = 8
    RADIUS_LG: Final[int] = 12
    RADIUS_XL: Final[int] = 16
    
    # Component sizes
    BUTTON_HEIGHT: Final[int] = 48
    INPUT_HEIGHT: Final[int] = 44
    ICON_SM: Final[int] = 16
    ICON_MD: Final[int] = 24
    ICON_LG: Final[int] = 32


@dataclass(frozen=True)
class AppConfig:
    """Application-wide configuration."""
    
    APP_NAME: Final[str] = "PRISMA"
    APP_VERSION: Final[str] = "2.0.0"
    APP_SUBTITLE: Final[str] = "Investigación Automatizada"
    
    # Window settings
    WINDOW_WIDTH: Final[int] = 1200
    WINDOW_HEIGHT: Final[int] = 800
    WINDOW_MIN_WIDTH: Final[int] = 900
    WINDOW_MIN_HEIGHT: Final[int] = 600
    
    # Model settings
    MODEL_FILENAME: Final[str] = "qwen2.5-3b-instruct-q4_k_m.gguf"
    MODEL_HF_REPO: Final[str] = "Qwen/Qwen2.5-3B-Instruct-GGUF"
    MODEL_SIZE_GB: Final[float] = 1.8


# Singleton instances for easy import
COLORS = Colors()
TYPOGRAPHY = Typography()
SPACING = Spacing()
CONFIG = AppConfig()