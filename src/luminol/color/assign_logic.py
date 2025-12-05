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
LIGHT_MAX_SATURATION_FG_TERTIARY = 0.2

# thresholds to ensure readable text
# Based on testing
DARK_FG_PRIMARY_LUMA_THRESHOLD = 90

# Darken the darkest extracted color by 30% to ensure deep backgrounds
# and better contrast with UI elements
DARK_BG_DARKEN_AMOUNT = 0.3  # 30%
ACCENT_MIN_COVERAGE_RATIO = 0.10


def _assign_bg(color_data: list[ColorData], theme: str) -> tuple[RGB, RGB]:
    """
    Assign primary and secondary background colors.

    Background hierarchy creates visual depth:
    - Primary: Main application surface (deepest layer)
    - Secondary: Slightly elevated surfaces (toolbars, sidebars)

    Args:
        color_data: List of ColorData sorted by luminance (brightest to darkest)
        theme: "dark" or "light"

    Returns:
        Tuple of (primary_bg, secondary_bg)
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

    return primary, secondary


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
                # generates a bright, desaturated text color for dark backgrounds.
                primary = blend(NEUTRAL_WHITE, bg_primary, 0.2)
                logging.warning(
                    "Could not achieve target contrast for primary fg, using white fallback"
                )

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

    # --- Secondary and Tertiary Foreground ---

    # For secondary text, the blend direction is based on the main theme
    secondary_blend_col = NEUTRAL_WHITE if theme == "dark" else NEUTRAL_BLACK

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

    # if bg_tertiary.luma > 90: # this gives better results for light theme
    if bg_tertiary.hsv.v > 0.65:
        # If bg_tertiary is light, text should be dark
        tert_blend_col = NEUTRAL_BLACK
    else:
        # If bg_tertiary is dark, text should be light
        tert_blend_col = NEUTRAL_WHITE

    # Use bg_primary as a neutral base to create the tertiary text color
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
            tertiary = blend(bg_primary, tert_blend_col, 0.6)
            # Fallback: Simple blend if optimization fails
            post_contrast = contrast_ratio(tertiary.luma, bg_tertiary.luma)
            if post_contrast < TERTIARY_CONTRAST_TARGET:
                blend_ratio = find_optimal_blend(
                    base_col=bg_primary,
                    blend_col=tert_blend_col,
                    contrast_with=bg_tertiary,
                    target_contrast=TERTIARY_CONTRAST_TARGET
                    - 1,  # at least try to achieve some contrast
                )
                if blend_ratio > 0:
                    tertiary = blend(bg_primary, tert_blend_col, blend_ratio)

                else:
                    tertiary = blend(bg_primary, tert_blend_col, 0.8)

    # Saturation control for light theme tertiary text on potentially dark bg
    if theme == "light" and tertiary.hsv.s > LIGHT_MAX_SATURATION_FG_TERTIARY:
        tertiary = blend(tertiary, tert_blend_col, 0.9)
        # tertiary = saturate(tertiary, 0.3)

    return primary, secondary, tertiary


def _select_vibrant_color(color_data: list[ColorData]) -> tuple[ColorData, RGB]:
    """
    Selects the most suitable vibrant color for accents and key surfaces.

    - Primary factor: Saturation * Value score (highest wins)
    - Value >= 0.6 is critical (90% of selected colors)
    - Luma between 30-130 (100% of selected colors with luma data)
    - Prefer Saturation >= 0.4 (70% of selected colors)
    - Coverage is NOT important (80% have low coverage)
    - Hue difference from max coverage: avg 66°, median 74° (prefer different hues)

    Args:
        color_data: List of ColorData sorted by luminance (brightest to darkest).
        theme: "dark" or "light".

    Returns:
        A tuple containing:
        - The original ColorData object that was selected.
        - The final, processed RGB color for the accent.
    """
    # Filter criteria based on analysis
    MIN_VALUE = 0.56  # Adjusted: WP 9 had V=0.56, most have V >= 0.6
    MIN_LUMA = 30  # All selected colors have luma >= 30
    MAX_LUMA = 130  # All selected colors have luma <= 130
    PREFERRED_MIN_SATURATION = 0.4  # 70% of selected colors have S >= 0.4

    # Find color with maximum coverage (dominant color)
    max_coverage_color = max(color_data, key=lambda c: c.coverage)
    max_coverage_hue = max_coverage_color.rgb.hsl.h * 360  # Convert to degrees

    def hue_distance(h1: float, h2: float) -> float:
        """Calculate circular distance between two hues (0-360 degrees)."""
        diff = abs(h1 - h2)
        return min(diff, 360 - diff)

    # Filter candidates: must have Value >= 0.56 and Luma in range
    candidates = []
    for color in color_data:
        hsv = color.rgb.hsv
        luma = color.rgb.luma

        # Primary filter: Value and Luma must be in acceptable range
        if hsv.v >= MIN_VALUE and MIN_LUMA <= luma <= MAX_LUMA:
            candidates.append(color)

    if not candidates:
        # Fallback: relax Value requirement further
        logging.warning(
            "No ideal vibrant color candidates found, using fallback logic."
        )
        candidates = [
            c
            for c in color_data
            if c.rgb.hsv.v >= 0.50 and MIN_LUMA <= c.rgb.luma <= MAX_LUMA
        ]

    if not candidates:
        # Final fallback: use S*V score on all colors
        candidates = color_data
        if not candidates:
            fallback_obj = color_data[len(color_data) // 2]
            return fallback_obj, fallback_obj.rgb  # Absolute fallback

    # Score candidates using multiple factors
    # Analysis showed 6/10 selected colors had highest S*V score
    # Also: avg hue diff from max coverage = 66°, median = 74°
    scored_candidates = []
    for color in candidates:
        saturation = color.rgb.hsv.s
        value = color.rgb.hsv.v
        hue = color.rgb.hsl.h * 360  # Convert to degrees

        # Primary score: S * V (this is the strongest indicator)
        primary_score = saturation * value

        # Bonus for preferred saturation range (S >= 0.4)
        saturation_bonus = 0.1 if saturation >= PREFERRED_MIN_SATURATION else 0.0

        # Hue difference bonus: prefer colors different from max coverage color
        # Analysis: avg diff = 66°, median = 74°
        # Stronger bonus for medium distances (40-100°) to avoid similar hues
        hue_diff = hue_distance(hue, max_coverage_hue)
        if hue_diff < 15:
            # Very close to max coverage: penalty (avoid similar colors)
            hue_bonus = -0.10
        elif 40 <= hue_diff <= 100:
            # Optimal range: strong bonus for good contrast
            hue_bonus = 0.10
        elif 20 <= hue_diff < 40:
            # Approaching optimal: gradual increase
            hue_bonus = 0.05 * ((hue_diff - 20) / 20)
        elif 100 < hue_diff <= 120:
            # Still good but decreasing
            hue_bonus = 0.10 * (1 - (hue_diff - 100) / 20)
        else:
            # Very far (>120°): small bonus
            hue_bonus = 0.03

        # Total score
        total_score = primary_score + saturation_bonus + hue_bonus

        scored_candidates.append((total_score, color))

    # Return the color object with the highest score
    best_color_obj = max(scored_candidates, key=lambda item: item[0])[1]

    # Post-process to guarantee minimum vibrancy
    processed_rgb = best_color_obj.rgb
    final_saturation = processed_rgb.hsv.s
    if final_saturation < 0.25:
        processed_rgb = saturate(processed_rgb, 1.5)  # Boost muted colors
    elif final_saturation > 0.85:
        processed_rgb = saturate(
            processed_rgb, 0.9
        )  # Slightly tone down very saturated colors

    return best_color_obj, processed_rgb


def _assign_accents(color_data: list[ColorData], theme: str) -> tuple[RGB, RGB]:
    """
    Selects a primary and a secondary accent color from the color data.

    It works by first selecting the most vibrant color as the primary accent.
    Then, it removes that color from the list and selects the next most
    vibrant color as the secondary accent.

    Args:
        color_data: List of ColorData sorted by luminance.
        theme: "dark" or "light".

    Returns:
        A tuple containing (primary_accent, secondary_accent).
    """
    # Select the primary accent.
    primary_accent_obj, primary_accent = _select_vibrant_color(color_data)

    # Create a new list of colors excluding the one that was just picked.
    # A copy is made to avoid modifying the original list.
    remaining_colors = [c for c in color_data if c != primary_accent_obj]

    # Select the secondary accent from the remaining colors.
    # We only need the processed RGB, so we discard the object.
    if not remaining_colors:
        # Fallback: if list is empty, derive from primary (old logic)
        secondary_accent = brighten(primary_accent, 1.2 if theme == "dark" else 0.9)
    else:
        _, secondary_accent = _select_vibrant_color(remaining_colors)

    return primary_accent, secondary_accent


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
