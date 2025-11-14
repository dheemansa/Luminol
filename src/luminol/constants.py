"""
This file contains centralized constants used throughout the Luminol application.
"""

# All available semantic and ANSI color names that can be used as sources
AVAILABLE_COLORS = (
    "bg-primary",
    "bg-secondary",
    "bg-tertiary",
    "text-primary",
    "text-secondary",
    "text-tertiary",
    "accent-primary",
    "accent-secondary",
    "error-color",
    "warning-color",
    "success-color",
    "border-active",
    "border-inactive",
    "ansi-0",  # Black
    "ansi-1",  # Red
    "ansi-2",  # Green
    "ansi-3",  # Yellow
    "ansi-4",  # Blue
    "ansi-5",  # Magenta
    "ansi-6",  # Cyan
    "ansi-7",  # White
    "ansi-8",  # Bright Black
    "ansi-9",  # Bright Red
    "ansi-10",  # Bright Green
    "ansi-11",  # Bright Yellow
    "ansi-12",  # Bright Blue
    "ansi-13",  # Bright Magenta
    "ansi-14",  # Bright Cyan
    "ansi-15",  # Bright White
)

# All supported color format strings for output
SUPPORTED_COLOR_FORMATS = (
    "hex6",
    "hex8",
    "rgb",
    "rgba",
    "rgb_decimal",
    "rgba_decimal",
)

VALID_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
