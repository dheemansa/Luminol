"""
This file contains the core logic for assigning specific roles
(e.g., background, foreground, accent) to a sorted list of colors.

Color Role Architecture:
- Backgrounds: primary (main surface), secondary (slightly elevated), tertiary (most elevated - cards/modals)
- Foregrounds: primary (main text), secondary (less prominent text), tertiary (text on elevated surfaces)
- Accents: primary (buttons/links), secondary (hover states)
- Borders: active (focused elements), inactive (neutral dividers)

Note on Comments:
Some comments in this file may refer to colors using a C1, C2...C8 notation.
This is a shorthand based on the assumption that the input `color_data` list
contains exactly 8 colors, sorted by luminance in ascending order:
- C1: The lightest color (color_data[0])
- C2: The second lightest color (color_data[1])
...
- C8: The darkest color (color_data[7])
"""

import logging

from ..core.data_types import ColorData, RGB
from .color_math import blend, contrast_ratio, find_optimal_blend
from .transformation import brighten, saturate

# Neutral colors for blending - slightly off pure white/black for better aesthetics
NEUTRAL_WHITE = RGB(238, 238, 238)
NEUTRAL_BLACK = RGB(18, 18, 18)

# at least 20% coverage to be considered "prominent"
# this gives the fg a nice touch of accent like color
FG_PRIMARY_COVERAGE_THRESHOLD = 0.2

# to ensure text visibility
MIN_CONTRAST_PRIMARY = 6  # Primary text - strictest for maximum readability
SECONDARY_CONTRAST_TARGET = 4.5  # Secondary text - WCAG AA standard
TERTIARY_CONTRAST_TARGET = 5  # Text on elevated surfaces - slightly higher than AA

# Limit foreground saturation to 30% to ensure it is not very vibrant
MAX_SATURATION_FG_PRIMARY = 0.3
LIGHT_MAX_SATURATION_FG_TERTIARY = 0.4

# thresholds to ensure readable text
# Based on testing
DARK_FG_PRIMARY_LUMA_THRESHOLD = 90

# Darken the darkest extracted color by 30% to ensure deep backgrounds
# and better contrast with UI elements
DARK_BG_DARKEN_AMOUNT = 0.3  # 30%
ACCENT_MIN_COVERAGE_RATIO = 0.10


def _assign_bg(color_data: list[ColorData], theme: str) -> tuple[RGB, RGB, RGB]:
    """
    Assign primary, secondary, and tertiary background colors.

    Background hierarchy creates visual depth:
    - Primary: Main application surface (deepest layer)
    - Secondary: Slightly elevated surfaces (toolbars, sidebars)
    - Tertiary: Most elevated surfaces (cards, modals, tooltips)

    Args:
        color_data: List of ColorData sorted by luminance (brightest to darkest)
        theme: "dark" or "light"

    Returns:
        Tuple of (primary_bg, secondary_bg, tertiary_bg)
    """
    if theme == "dark":
        # Primary: Use the darkest color and darken it further for depth
        primary = brighten(
            color_data[-1].rgb, 1 - DARK_BG_DARKEN_AMOUNT
        )  # make the darkest color slighly darker

        # Secondary: Create a slightly lighter background for hierarchy
        secondary_candidate = color_data[-2].rgb  # 2nd darkest color
        luma_diff = secondary_candidate.luma - primary.luma
        hue_diff = abs(secondary_candidate.hsv.h - primary.hsv.h) * 360  # in degrees

        # If too similar in brightness, brighten to create clear hierarchy
        if luma_diff < 4:
            secondary = brighten(secondary_candidate, 1.4)

        # If very different in color/brightness, use brightened primary for consistency
        elif luma_diff > 10 and hue_diff > 20:
            secondary = brighten(primary, 1.6)

        else:
            secondary = secondary_candidate

        # Tertiary: Most elevated surfaces - pick a saturated lighter color
        # This creates visual "pop" for cards and elevated elements
        tert_candidate = color_data[2:-3]  # C2 to C5, lighter mid-range colors
        tertiary = max(tert_candidate, key=lambda col: col.coverage * col.rgb.hsv.s).rgb

        # Ensure tertiary is bright enough to stand out from primary/secondary
        if tertiary.luma < 50:
            logging.debug("Tertiary bg too dark, brightening")
            # tertiary = brighten(tertiary, 1.5)
            tertiary = blend(tertiary, NEUTRAL_WHITE, 0.3)

    else:  # Light theme
        # Primary: Pick the brightest color with high coverage
        # this eliminates non-dominant colors which are light
        primary = max(
            color_data[:3], key=lambda col: col.coverage
        ).rgb  # col with highest coverage among top 3 brightest color

        # Desaturate if too vibrant - light backgrounds should be subtle
        if primary.hsl.s > 0.5:
            # TODO: need to test this
            primary = saturate(primary, 0.7)

        # Ensure primary is bright enough for a light theme
        if primary.luma < 120:
            primary = brighten(primary, 1.5)

        # Secondary: Slightly lighter than primary for elevated surfaces
        # Creates subtle depth in light themes (e.g., cards slightly lifted)
        secondary = blend(primary, NEUTRAL_WHITE, 0.4)

        # Tertiary: Darker, saturated color for maximum elevation effect
        tert_candidate = color_data[3:-1]  # C3 to C7, darker colors
        tertiary = max(tert_candidate, key=lambda col: col.coverage * col.rgb.hsv.s).rgb

    return primary, secondary, tertiary


def _assign_fg(
    color_data: list[ColorData],
    bg_primary: RGB,
    bg_secondary: RGB,
    bg_tertiary: RGB,
    theme: str,
) -> tuple[RGB, RGB, RGB]:
    """
    Assign primary, secondary, and tertiary foreground (text) colors.

    Foreground hierarchy creates text emphasis:
    - Primary: Main body text, headings (reads on bg_primary)
    - Secondary: Less prominent text like labels, timestamps (reads on bg_secondary)
    - Tertiary: Text on elevated surfaces like cards (reads on bg_tertiary)

    All foregrounds are adjusted to meet WCAG contrast requirements.

    Args:
        color_data: List of ColorData sorted by luminance (brightest to darkest)
        bg_primary, bg_secondary, bg_tertiary: Background colors to contrast against
        theme: "dark" or "light"

    Returns:
        Tuple of (primary_fg, secondary_fg, tertiary_fg)
    """
    primary_candidate = None
    if theme == "dark":
        # Strategy: Find a prominent bright color for text on dark backgrounds
        # Look in the brighter half of the palette
        for col in color_data[: len(color_data) // 2]:
            if col.coverage > FG_PRIMARY_COVERAGE_THRESHOLD:
                primary_candidate = col.rgb
                break

        # Fallback: if no prominent color found, use the least saturated color from the top 3 brightest
        if primary_candidate is None:
            primary_candidate = min(color_data[:3], key=lambda col: col.rgb.hsv.s).rgb

        pre_contrast = contrast_ratio(primary_candidate.luma, bg_primary.luma)

        logging.debug("Pre-contrast ratio (dark theme): %.2f", pre_contrast)

        # Check if candidate already meets contrast requirements
        if pre_contrast >= MIN_CONTRAST_PRIMARY:
            primary = primary_candidate

        else:
            # Adjust candidate by blending toward white to increase contrast
            blend_ratio = find_optimal_blend(
                base_col=primary_candidate,
                blend_col=NEUTRAL_WHITE,
                contrast_with=bg_primary,
                target_contrast=MIN_CONTRAST_PRIMARY,
            )

            if blend_ratio > 0:
                primary = blend(
                    color=primary_candidate,
                    blend_with=NEUTRAL_WHITE,
                    amount=blend_ratio,
                )
            else:
                # Edge case: If optimization fails, use candidate as-is
                # Post-processing can fix this
                logging.warning("Could not achieve target contrast for primary fg")
                primary = primary_candidate

        # Limit saturation to ensure it is close to whitish
        if primary.hsv.s > MAX_SATURATION_FG_PRIMARY:
            primary = blend(primary, NEUTRAL_WHITE, 0.3)

        # TODO: Revisit green hue handling - needs more testing

        # # 90 and 150 are lower and higher limit of green hue(in degrees)
        # primary_hue = primary.hsv.h * 360  # in degrees
        # print("hue: ", primary_hue)
        # if 75 < primary_hue and primary_hue < 150:
        #     # necessary becauase green to more sensitive to the human eye
        #     if primary.hsv.s > 0.3:
        #         primary = blend(primary, NEUTRAL_WHITE, 0.5)

        # Ensure minimum brightness for readability on dark backgrounds
        if primary.luma < DARK_FG_PRIMARY_LUMA_THRESHOLD:
            primary = blend(primary, NEUTRAL_WHITE, 0.3)

    else:  # Light theme
        # Look in the darker half of the palette, starting from darkest
        for col in reversed(color_data[len(color_data) // 2 :]):
            if col.coverage > FG_PRIMARY_COVERAGE_THRESHOLD:
                primary_candidate = col.rgb
                break

        # Fallback: if no prominent color is found, use the darkest color.
        if primary_candidate is None:
            primary_candidate = color_data[-1].rgb

        pre_contrast = contrast_ratio(bg_primary.luma, primary_candidate.luma)
        logging.debug("pre Contrast Ratio (light theme): %.2f", pre_contrast)

        if pre_contrast >= MIN_CONTRAST_PRIMARY:
            primary = primary_candidate
        else:
            # Adjust candidate by blending toward black to increase contrast
            blend_ratio = find_optimal_blend(
                base_col=primary_candidate,
                blend_col=NEUTRAL_BLACK,
                contrast_with=bg_primary,
                target_contrast=MIN_CONTRAST_PRIMARY,
            )

            if blend_ratio > 0:
                primary = blend(
                    color=primary_candidate,
                    blend_with=NEUTRAL_BLACK,
                    amount=blend_ratio,
                )
            else:
                # Fallback: Use black tinted slightly with background color
                primary = blend(NEUTRAL_BLACK, bg_primary, 0.2)
                logging.warning(
                    "Could not achieve target contrast, using black fallback"
                )

        # Limit saturation for light theme
        if primary.hsv.s > MAX_SATURATION_FG_PRIMARY:
            primary = blend(primary, NEUTRAL_BLACK, 0.3)

    # set blend direction for secondary/tertiary text
    if theme == "dark":
        # Dark theme: secondary text blends toward white (brighter = more prominent)
        # tertiary fg blends toward black (darker for contrast with lighter tertiary bg)
        secondary_blend_col = NEUTRAL_WHITE
        tert_blend_col = NEUTRAL_BLACK
    else:
        # Light theme: secondary text blends toward black (darker = more prominent)
        # tertiary fg blends toward white (lighter for contrast with darker tertiary bg)
        secondary_blend_col = NEUTRAL_BLACK
        tert_blend_col = NEUTRAL_WHITE

    # secondary

    # Using candidate to preserve original color character - 'primary' has been
    # heavily adjusted for contrast/saturation and lost its distinctive hue
    pre_secondary_contrast = contrast_ratio(primary_candidate.luma, bg_secondary.luma)

    if pre_secondary_contrast >= SECONDARY_CONTRAST_TARGET:
        secondary = primary_candidate

    else:
        secondary_blend_ratio = find_optimal_blend(
            base_col=primary_candidate,
            blend_col=secondary_blend_col,
            contrast_with=bg_secondary,
            target_contrast=SECONDARY_CONTRAST_TARGET,
        )

        if secondary_blend_ratio > 0:
            secondary = blend(
                primary_candidate, secondary_blend_col, secondary_blend_ratio
            )
        else:
            # Fallback: Simple blend toward neutral
            secondary = blend(primary_candidate, secondary_blend_col, 0.5)

    # Use bg_primary as base - it naturally contrasts with bg_tertiary (elevated surfaces)
    pre_tertiary_contrast = contrast_ratio(bg_primary.luma, bg_tertiary.luma)

    if pre_tertiary_contrast >= TERTIARY_CONTRAST_TARGET:
        tertiary = bg_primary
    else:
        tert_blend_ratio = find_optimal_blend(
            base_col=bg_primary,
            blend_col=tert_blend_col,
            contrast_with=bg_tertiary,
            target_contrast=TERTIARY_CONTRAST_TARGET,
        )
        if tert_blend_ratio > 0:
            tertiary = blend(bg_primary, tert_blend_col, tert_blend_ratio)
        else:
            # Fallback: Simple blend
            tertiary = blend(bg_primary, tert_blend_col, 0.5)

    # Additional saturation control for light theme tertiary text
    # to ensure it is not very vibrant
    if theme == "light" and tertiary.hsv.s > LIGHT_MAX_SATURATION_FG_TERTIARY:
        tertiary = blend(tertiary, tert_blend_col, 0.3)

    return primary, secondary, tertiary


def _assign_accent(color_data: list[ColorData], theme_type: str) -> tuple[RGB, RGB]:
    """
    Assign primary and secondary accent colors.

    Accents are used for:
    - Primary: Buttons, links, active states, brand elements
    - Secondary: Hover states, focus rings, highlights

    Strategy: Pick the most saturated color to create visual emphasis.

    Args:
        color_data: List of ColorData sorted by luminance (brightest to darkest)
        theme_type: "dark" or "light"

    Returns:
        Tuple of (primary_accent, secondary_accent)
    """
    if theme_type == "dark":
        # Avoid extremes: skip C1 (too bright) and C7-C8 (too dark for visibility)
        primary_candidate = color_data[1:-2]

        # Pick the most saturated color for maximum visual impact
        primary = max(
            primary_candidate,
            # key=lambda col: col.rgb.hsv.s * col.rgb.hsv.v,
            key=lambda col: col.rgb.hsv.s,
        ).rgb

        # Ensure accent is bright enough to stand out on dark backgrounds
        if primary.luma < 80:
            primary = brighten(primary, 1.8)
            primary = saturate(primary, 1.2)

    else:
        # Skip C1-C3 (too light for visibility) and C8 (reserved for text
        primary = max(
            color_data[3:-1], key=lambda col: col.rgb.hsv.s
        ).rgb  # omit C1 to C3 and C8

    # Boost saturation if accent is too muted
    # Accents should be vibrant to draw attention
    if primary.hsv.s < 0.2:
        primary = saturate(primary, 2.0)
    elif primary.hsv.s < 0.4:
        primary = saturate(primary, 1.8)

    # secondary(TODO: needs improvement)
    if theme_type == "dark":
        # Make it brighter and slightly more saturated than primary
        brighter_accent = brighten(primary, 1.2)
        secondary = saturate(brighter_accent, 1.1)
    else:  # Light theme
        # Make it slightly darker for subtle differentiation
        secondary = brighten(primary, 0.9)

    return primary, secondary


def _assign_border(accent_primary: RGB, bg_primary: RGB) -> tuple[RGB, RGB]:
    """
    Assign active and inactive border colors.

    Borders are used for:
    - Active: Focused inputs, selected items, active navigation
    - Inactive: Dividers, neutral separators, unfocused inputs

    Args:
        accent_primary: The primary accent color of the theme
        bg_primary: The primary background color of the theme

    Returns:
        Tuple of (active_border, inactive_border)
    """
    # Active border: Use accent color directly for maximum visibility
    active_border = accent_primary

    # Inactive border: Blend accent with background for subtlety
    # Then desaturate to make it more neutral
    mixed_accent = blend(accent_primary, bg_primary, 0.5)
    inactive_border = saturate(mixed_accent, 0.5)

    return active_border, inactive_border


def _assign_ansi_colors() -> tuple[RGB, ...]:
    """
    Returns a hardcoded set of 16 ANSI colors based on the Catppuccin Latte
    theme. The bright variants are generated by brightening the base colors.
    """
    # Catppuccin Latte colors as the base for normal ANSI colors
    latte = (
        RGB(76, 79, 105),  # Black
        RGB(210, 15, 57),  # Red
        RGB(64, 160, 43),  # Green
        RGB(223, 142, 29),  # Yellow
        RGB(30, 102, 245),  # Blue
        RGB(234, 118, 203),  # Magenta
        RGB(4, 165, 229),  # Cyan
        RGB(188, 192, 204),  # White
    )

    # Bright variants are generated by brightening the normal ones by 20%
    bright_factor = 1.2
    bright_latte = tuple(brighten(c, bright_factor) for c in latte)

    return latte + bright_latte
