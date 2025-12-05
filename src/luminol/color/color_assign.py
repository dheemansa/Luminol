import logging

from ..core.data_types import ColorData, RGB
from .assign_logic import _assign_bg, _assign_border, _assign_fg, _assign_accents
from .color_math import contrast_ratio

THEME_THRESHOLD = 128  # ~ 255/2


def decide_theme(color_data: list[ColorData]) -> str:
    """
    Decide whether a palette suggests a light or dark theme.

    Args:
        color_data: dict mapping RGB tuples to dict with "coverage" and "luma" keys

    Returns:
        "light" or "dark"
    """

    # Weighted luma calculation
    weighted_luma = sum(col.rgb.luma * col.coverage for col in color_data)

    print(f"Weighted luma: {weighted_luma:.2f}")

    return "light" if weighted_luma > THEME_THRESHOLD else "dark"


def assign_color(
    color_data: list[ColorData], theme_type: str = "auto", presorted: bool = False
) -> dict[str, RGB]:
    """
    Generate a color theme from extracted colors.

    Args:
        color_data: List of ColorData objects. Must be sorted by decreasing luma
                   (brightest to darkest). Recommended to use 8 dominant colors for best results.
        theme_type: Theme variant - "auto" (detect from colors), "light", or "dark

    Returns:
        A dictionary mapping color role names (e.g., 'bg-primary', 'ansi-1')
        to their assigned RGB color objects.
    """

    MIN_COLORS = 8
    if len(color_data) < MIN_COLORS:
        raise ValueError(
            f"Need at least {MIN_COLORS} colors for theme generation, got {len(color_data)}."
        )

    SUPPORTED_THEME_TYPES = ("auto", "light", "dark")
    if theme_type not in SUPPORTED_THEME_TYPES:
        raise ValueError(
            f"'{theme_type}' is not a valid theme type. Supported option are {', '.join(SUPPORTED_THEME_TYPES)}"
        )

    if not presorted:
        # sort in decreasing order
        color_data = sorted(color_data, key=lambda c: c.rgb.luma, reverse=True)

    if theme_type == "auto":
        theme = decide_theme(color_data=color_data)
    else:
        theme = theme_type

    logging.debug("Theme Type: %s", theme)

    bg_primary, bg_secondary = _assign_bg(color_data, theme)

    # Select a single vibrant color to be used for accents and elevated surfaces
    accent_primary, accent_secondary = _assign_accents(color_data, theme=theme)
    bg_tertiary = accent_primary
    type(accent_primary)

    fg_primary, fg_secondary, fg_tertiary = _assign_fg(
        color_data, bg_primary, bg_secondary, bg_tertiary, theme=theme
    )
    active_border, inactive_border = _assign_border(accent_primary, bg_primary)

    logging.debug(
        "Post Contrast Ratio: %.2f",
        contrast_ratio(bg_primary.luma, fg_primary.luma),
    )

    # --- Construct Final Theme Dictionary ---
    theme_dict = {
        "bg-primary": bg_primary,
        "bg-secondary": bg_secondary,
        "bg-tertiary": bg_tertiary,
        "text-primary": fg_primary,
        "text-secondary": fg_secondary,
        "text-tertiary": fg_tertiary,
        "accent-primary": accent_primary,
        "accent-secondary": accent_secondary,
        "border-active": active_border,
        "border-inactive": inactive_border,
    }

    # TODO: assign proper error,... colors
    if theme == "dark":
        theme_dict["error-color"] = RGB(243, 139, 168)
        theme_dict["warning-color"] = RGB(250, 179, 135)
        theme_dict["success-color"] = RGB(166, 227, 161)
    else:  # light theme
        theme_dict["error-color"] = RGB(243, 139, 168)
        theme_dict["warning-color"] = RGB(250, 179, 135)
        theme_dict["success-color"] = RGB(166, 227, 161)

    return theme_dict
