import logging

from ..core.data_types import ColorData, RGB
from .color_computation import (
    _find_optimal_blend_for_contrast,
    _is_near_white,
    blend,
    contrast_ratio,
    luma,
)


def _darken(color: RGB, amount: float) -> RGB:
    factor = 1 - amount

    r_final = round(color.r * factor)
    g_final = round(color.g * factor)
    b_final = round(color.b * factor)

    return RGB(r_final, g_final, b_final)


# TODO: move this function to a different file after testing is done
def apply_terminal_colors(bg: RGB, fg: RGB):
    """
    Apply background and foreground colors to terminal using OSC sequences.

    Args:
        bg: Background RGB color
        fg: Foreground RGB color
    """
    # Convert RGB to hex format
    bg_hex = f"#{bg.r:02x}{bg.g:02x}{bg.b:02x}"
    fg_hex = f"#{fg.r:02x}{fg.g:02x}{fg.b:02x}"

    # OSC sequences for terminal colors
    # \033 is ESC, ]10; sets foreground, ]11; sets background
    print(f"\033]10;{fg_hex}\033\\", end="")  # Foreground
    print(f"\033]11;{bg_hex}\033\\", end="")  # Background

    # Optional: Also set cursor color to match foreground
    print(f"\033]12;{fg_hex}\033\\", end="")  # Cursor color


def decide_theme(color_data: list[ColorData]) -> str:
    """
    Decide whether a palette suggests a light or dark theme.

    Args:
        color_data: dict mapping RGB tuples to dict with "coverage" and "luma" keys

    Returns:
        "light" or "dark"
    """

    THEME_THRESHOLD = 120

    # Weighted luma calculation
    weighted_luma = sum(col.rgb.luma * col.coverage for col in color_data)

    print(f"Weighted luma: {weighted_luma:.2f}")

    return "light" if weighted_luma > THEME_THRESHOLD else "dark"


def _assign_bg(color_data: list[ColorData], theme: str) -> RGB:
    if theme == "dark":
        bg_primary = _darken(
            color_data[-1].rgb, 0.3
        )  # make the darkest color slighly darker
    else:
        # TODO: improve this
        bg_primary = color_data[0].rgb  # lightest color is the bg
    return bg_primary  # TODO: return primay, secondary, tertiary


def _assign_fg(
    color_data: list[ColorData],
    bg_primary: RGB,
    bg_secondary: RGB,
    bg_tertiary: RGB,
    theme: str,
) -> RGB:
    FG_PRIMARY_COVERAGE_THRESHOLD = 0.2
    MIN_CONTRAST = 6
    NEUTRAL_WHITE = RGB(238, 238, 238)

    fg_primary_candidate_color = None
    mid_index = len(color_data) // 2

    if theme == "dark":
        bg_primary_coverage: float = color_data[-1].coverage
    else:
        bg_primary_coverage = color_data[0].coverage

    for col in color_data[:mid_index]:
        relative_coverage = col.coverage / bg_primary_coverage
        if relative_coverage > FG_PRIMARY_COVERAGE_THRESHOLD:
            fg_primary_candidate_color = col
            break

    # If no prominent color found, use the brightest
    if fg_primary_candidate_color is None:
        fg_primary_candidate_color = color_data[0]  # brightest

    pre_contrast = contrast_ratio(fg_primary_candidate_color.rgb.luma, bg_primary.luma)

    logging.debug("pre Contrast Ratio: %.2f", pre_contrast)

    if pre_contrast >= MIN_CONTRAST:
        fg_primary = fg_primary_candidate_color.rgb

    else:
        blend_ratio = _find_optimal_blend_for_contrast(
            target_contrast=MIN_CONTRAST,
            darker_rgb=bg_primary,
            lighter_rgb=fg_primary_candidate_color.rgb,
            brighten_toward=NEUTRAL_WHITE,
        )

        fg_primary = blend(
            color=fg_primary_candidate_color.rgb,
            blend_with=NEUTRAL_WHITE,
            amount=blend_ratio,
        )

    if not _is_near_white(fg_primary, 60):
        logging.debug("Before White correction fg: %s", fg_primary)
        fg_primary = blend(
            color=fg_primary,
            blend_with=NEUTRAL_WHITE,
            amount=0.3,  # small value because fg has alrady passed the contrast
        )

    return fg_primary  # TODO: return primay, secondary, tertiary


def assign_color(color_data: list[ColorData], theme_type: str = "auto"):
    """
    color_data has to be sorted by decreasing luma
    """

    SUPPORTED_THEME_TYPES = ("auto", "light", "dark")
    if theme_type not in SUPPORTED_THEME_TYPES:
        raise ValueError(
            f"'{theme_type}' is not a valid theme type. Supported option are {', '.join(SUPPORTED_THEME_TYPES)}"
        )

    darkest = color_data[-1].rgb
    lightest = color_data[0].rgb

    if theme_type == "auto":
        theme = decide_theme(color_data=color_data)
    else:
        theme = theme_type

    logging.debug("Theme Type: %s", theme)

    if theme == "dark":
        bg_primary = _assign_bg(color_data, "dark")
        logging.debug("Background color: %s", bg_primary)

        bg_secondary = RGB(0, 0, 0)
        bg_tertiary = RGB(0, 0, 0)
        fg_primary = _assign_fg(
            color_data, bg_primary, bg_secondary, bg_tertiary, theme="dark"
        )

        logging.debug("Text color: %s", fg_primary)

    else:  # for light theme
        bg_primary = lightest
        logging.debug("Background color: %s", bg_primary)

        fg_primary = darkest
        logging.debug("Text color: %s", fg_primary)

    logging.debug(
        "Post Contrast Ratio: %.2f",
        contrast_ratio(
            luma(bg_primary.r, bg_primary.g, bg_primary.b),
            luma(fg_primary.r, fg_primary.g, fg_primary.b),
        ),
    )

    apply_terminal_colors(bg=bg_primary, fg=fg_primary)
