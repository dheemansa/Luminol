"""
This file contains centralized constants used
throughout the Luminol application.
"""

from .data_types import RGB

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

SUPPORTED_COLOR_TRANFORMATION = (
    "hue",
    "contrast",
    "saturation",
    "opacity",
    "temperature",
    "brightness",
)


VALID_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

TEST_PRESET: dict[str, RGB] = {
    "bg-primary": RGB(30, 30, 46),
    "bg-secondary": RGB(49, 50, 68),
    "bg-tertiary": RGB(69, 71, 90),
    "text-primary": RGB(205, 214, 244),
    "text-secondary": RGB(186, 194, 222),
    "accent-primary": RGB(138, 244, 218),
    "accent-secondary": RGB(243, 139, 168),
    "error-color": RGB(243, 139, 168),
    "warning-color": RGB(249, 226, 175),
    "success-color": RGB(166, 227, 161),
    "border-active": RGB(205, 214, 244),
    "border-inactive": RGB(49, 50, 68),
}
