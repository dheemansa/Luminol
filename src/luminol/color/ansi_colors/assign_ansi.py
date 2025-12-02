"""
Generates an image-aware 16-color ANSI theme by finding and
adjusting colors from the source image.
"""

import logging

from ...core.data_types import ColorData, HSV, RGB
from ..color_math import contrast_ratio
from ..transformation import brighten, saturate
from .python_4bit import generate_color_scheme
from ..assign_logic import _select_vibrant_color

#  Ensure minimum contrast for ANSI colors
MIN_ANSI_CONTRAST = 2.0


def find_color_in_hue_range(
    color_data: list[ColorData],
    target_hue: float,
    hue_tolerance: float = 30.0,
    target_luma: float | None = None,
    luma_tolerance: float | None = None,
) -> ColorData | None:
    """
    Find a color from color_data that falls within the hue range.

    Args:
        color_data: list of ColorData objects from image
        target_hue: Target hue in degrees (0-360)
        hue_tolerance: How many degrees +/- to accept (default 30°)
        target_luma: Optional target luma to aim for
        luma_tolerance: Optional luma tolerance

    Returns:
        ColorData if found, None otherwise
    """
    target_hue = target_hue % 360
    candidates: list[tuple] = []

    for color in color_data:
        # Luma check
        if target_luma is not None and luma_tolerance is not None:
            luma = color.rgb.luma
            if not (
                target_luma - luma_tolerance <= luma <= target_luma + luma_tolerance
            ):
                continue  # Skip color if outside luma range

        hue = color.rgb.hsl.h * 360

        # Calculate circular distance
        diff = abs(hue - target_hue)
        distance = min(diff, 360 - diff)

        if distance <= hue_tolerance:
            # Add the color and its distance to the list of candidates
            candidates.append((distance, color))

    if not candidates:
        return None

    # Find the candidate with the minimum hue distance.
    # The first element of the tuple is the distance, so min() works correctly.
    _, best_match = min(candidates, key=lambda x: x[0])
    return best_match


def generate_ansi(
    color_data: list[ColorData],
    assigned_colors: dict[str, RGB],
) -> dict[str, RGB]:
    """
    Generate ANSI color scheme that uses actual image colors when possible.

    Args:
        color_data: List of ColorData from image extraction
        assigned_colors: Dictionary with accent, bg, and text colors
        generate_color_scheme: The 4bit color scheme generation function

    Returns:
        Dictionary with theme colors
    """
    accent = _select_vibrant_color(color_data, "dark")
    bright_lightness = max(assigned_colors.values(), key=lambda col: col.hsl.l).hsl.l
    saturation = accent.hsl.s if accent.hsl.s > 0.3 else 0.4

    base_theme = generate_color_scheme(
        normal_lightness=accent.hsl.l,
        bright_lightness=bright_lightness,
        saturation=saturation,
        dye_h=accent.hsl.h,
        dye_s=accent.hsl.s,
        dye_l=accent.hsl.l,
        dye_a=0.7,
        dye_type="color",
    )

    ansi_color_map = {
        "ansi-1": ("red", -15 + 0),  # red
        "ansi-2": ("green", -15 + 120),  # green
        "ansi-3": ("yellow", -15 + 60),  # yellow
        "ansi-4": ("blue", -15 + 240),  # blue
        "ansi-5": ("magenta", -15 + 300),  # magenta
        "ansi-6": ("cyan", -15 + 180),  # cyan
        "ansi-9": ("bright_red", -15 + 0),
        "ansi-10": ("bright_green", -15 + 120),
        "ansi-11": ("bright_yellow", -15 + 60),
        "ansi-12": ("bright_blue", -15 + 240),
        "ansi-13": ("bright_magenta", -15 + 300),
        "ansi-14": ("bright_cyan", -15 + 180),
    }

    # Find direct matches from the image and replace them
    for ansi_key, (color_name, target_hue) in ansi_color_map.items():
        matched_color = find_color_in_hue_range(
            color_data,
            target_hue,
            hue_tolerance=45,
            target_luma=accent.luma,
            luma_tolerance=accent.luma * 0.66,
        )

        if matched_color:
            logging.debug(
                "  %s: Found match (hue=%.1f°)",
                color_name,
                matched_color.rgb.hsl.h * 360,
            )
            is_bright = (
                ansi_key.startswith("ansi-") and int(ansi_key.split("-")[1]) >= 8
            )

            final_rgb = matched_color.rgb
            if is_bright:
                original_hsv = matched_color.rgb.hsv
                target_val = max(original_hsv.v, 0.75)

                # Only create a new color if the value needs to change
                if target_val != original_hsv.v:
                    new_hsv = HSV(original_hsv.h, original_hsv.s, target_val)
                    final_rgb = new_hsv.rgb

            base_theme[ansi_key] = final_rgb
        else:
            logging.debug("  %s: No match found, using generated color.", color_name)

    # Post-processing saturation boost
    logging.debug("\nApplying post-processing saturation boost...")
    emphasis_keys = ["ansi-1", "ansi-9", "ansi-2", "ansi-10", "ansi-3", "ansi-11"]
    for key, color in base_theme.items():
        if key in emphasis_keys:
            base_theme[key] = saturate(color, 1.5)  # Extra emphasis
        else:
            base_theme[key] = saturate(color, 1.3)  # Standard boost

    bg_luma = assigned_colors["bg-primary"].luma
    ansi_chroma_keys = [f"ansi-{i}" for i in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14]]

    for key in ansi_chroma_keys:
        color = base_theme[key]
        original_color_luma = color.luma

        iterations = 0
        max_iterations = 15  # Safety break

        while (
            contrast_ratio(color.luma, bg_luma) < MIN_ANSI_CONTRAST
            and iterations < max_iterations
        ):
            color = brighten(color, 1.05)  # Brighten color by 5%
            iterations += 1

        if color.luma != original_color_luma:
            logging.debug(
                "  Adjusted '%s' brightness for contrast (%s steps).", key, iterations
            )
            base_theme[key] = color

    return base_theme
