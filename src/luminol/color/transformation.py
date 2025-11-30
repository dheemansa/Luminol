"""
This module provides functions for performing color transformations
such as changing brightness, saturation, or hue.
"""

import colorsys
from typing import Optional
from ..core.data_types import RGB, RGBA


def saturate(color: RGB, factor: float) -> RGB:
    """
    Increase or decrease the saturation of a color.

    Args:
        color: The input RGB color object.
        factor: The saturation multiplier. > 1 increases saturation, < 1 decreases it.

    Returns:
        A new, transformed RGB object.
    """
    h, s, v = color.hsv.h, color.hsv.s, color.hsv.v
    new_s = max(0.0, min(1.0, s * factor))
    r, g, b = colorsys.hsv_to_rgb(h, new_s, v)
    return RGB(round(r * 255), round(g * 255), round(b * 255))


def brighten(color: RGB, factor: float) -> RGB:
    """
    Increase or decrease the brightness (value) of a color.

    Args:
        color: The input RGB color object.
        factor: The brightness multiplier. > 1 increases brightness, < 1 decreases it.

    Returns:
        A new, transformed RGB object.
    """
    h, s, v = color.hsv.h, color.hsv.s, color.hsv.v
    new_v = max(0.0, min(1.0, v * factor))
    r, g, b = colorsys.hsv_to_rgb(h, s, new_v)
    return RGB(round(r * 255), round(g * 255), round(b * 255))


def shift_hue(color: RGB, degrees: float) -> RGB:
    """
    Shift the hue of a color by a given number of degrees.

    Args:
        color: The input RGB color object.
        degrees: The number of degrees to shift the hue on the color wheel.

    Returns:
        A new, transformed RGB object.
    """
    h, s, v = color.hsv.h, color.hsv.s, color.hsv.v
    hue_shift = degrees / 360.0
    new_h = (h + hue_shift) % 1.0
    r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
    return RGB(round(r * 255), round(g * 255), round(b * 255))


def _adjust_contrast(r: int, g: int, b: int, factor: float) -> tuple[int, int, int]:
    """Adjusts the contrast of a color."""
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    r_new = (r_norm - 0.5) * factor + 0.5
    g_new = (g_norm - 0.5) * factor + 0.5
    b_new = (b_norm - 0.5) * factor + 0.5
    return (
        round(max(0, min(255, r_new * 255))),
        round(max(0, min(255, g_new * 255))),
        round(max(0, min(255, b_new * 255))),
    )


def _adjust_temperature(r: int, g: int, b: int, value: int) -> tuple[int, int, int]:
    """Adjusts the color temperature."""
    temp = max(-100, min(100, value)) / 100.0
    if temp > 0:
        r_new = r + (255 - r) * temp * 0.5
        b_new = b - b * temp * 0.3
    else:
        temp = abs(temp)
        b_new = b + (255 - b) * temp * 0.5
        r_new = r - r * temp * 0.3
    return (
        round(max(0, min(255, r_new))),
        g,
        round(max(0, min(255, b_new))),
    )


def _transform_color(
    rgb: RGB,
    hue: Optional[int] = None,
    saturation: Optional[float] = None,
    brightness: Optional[float] = None,
    contrast: Optional[float] = None,
    temp: Optional[int] = None,
    opacity: Optional[float] = None,
) -> RGBA:
    """
    Apply a chain of transformations to a color object, returning an RGBA.
    """
    # Start with a mutable tuple
    r, g, b = rgb.r, rgb.g, rgb.b

    # Apply HSV-based transformations first
    temp_rgb = RGB(r, g, b)
    if hue is not None:
        temp_rgb = shift_hue(temp_rgb, float(hue))
    if saturation is not None:
        temp_rgb = saturate(temp_rgb, saturation)
    if brightness is not None:
        temp_rgb = brighten(temp_rgb, brightness)

    r, g, b = temp_rgb.r, temp_rgb.g, temp_rgb.b

    # Apply RGB-based transformations
    if contrast is not None:
        r, g, b = _adjust_contrast(r, g, b, contrast)
    if temp is not None:
        r, g, b = _adjust_temperature(r, g, b, temp)

    # Handle opacity
    a = opacity if opacity is not None else 1.0
    a = max(0.0, min(1.0, a))

    return RGBA(r, g, b, a)
