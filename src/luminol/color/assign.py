import logging

from ..utils.data_types import ColorData, RGB
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
    weighted_luma = sum(col.luma * col.coverage for col in color_data)

    print(f"Weighted luma: {weighted_luma:.2f}")

    return "light" if weighted_luma > THEME_THRESHOLD else "dark"


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

    print(f"Theme Type: {theme}")

    if theme == "dark":
        bg = _darken(darkest, 0.5)
        bg_luma = luma(*bg)
        bg_coverage = color_data[-1].coverage
        print(f"Background color: {bg}")

        COVERAGE_THRESHOLD = 0.2
        MIN_CONTRAST = 6
        NEUTRAL_WHITE = RGB(238, 238, 238)

        fg_selected_color = None
        mid_index = len(color_data) // 2

        for col in color_data[:mid_index]:
            relative_coverage = col.coverage / bg_coverage
            if relative_coverage > COVERAGE_THRESHOLD:
                fg_selected_color = col
                break

        # If no prominent color found, use the brightest
        if fg_selected_color is None:
            fg_selected_color = color_data[0]

        pre_contrast = contrast_ratio(fg_selected_color.luma, bg_luma)

        print(f"pre Contrast Ratio: {pre_contrast:.2f}")

        if pre_contrast >= MIN_CONTRAST:
            fg = fg_selected_color.rgb

        else:
            blend_ratio = _find_optimal_blend_for_contrast(
                target_contrast=MIN_CONTRAST,
                darker_rgb=bg,
                lighter_rgb=fg_selected_color.rgb,
                brighten_toward=NEUTRAL_WHITE,
            )

            fg = blend(
                color=fg_selected_color.rgb,
                blend_with=NEUTRAL_WHITE,
                amount=blend_ratio,
            )

        if not _is_near_white(fg, 60):
            print(f"before white {fg}")
            logging.warning("not white using blend")
            fg = blend(
                color=fg,
                blend_with=NEUTRAL_WHITE,
                amount=0.3,  # small value because fg has alrady passed the contrast
            )

        print(f"Text color: {fg}")

    else:  # for light theme
        bg = lightest
        print(f"Background color: {bg}")

        fg = darkest
        print(f"Text color: {fg}")

    post_contrast = contrast_ratio(luma(bg.r, bg.g, bg.b), luma(fg.r, fg.g, fg.b))
    print(f"Post Contrast Ratio: {post_contrast:.2f}")

    apply_terminal_colors(bg=bg, fg=fg)
