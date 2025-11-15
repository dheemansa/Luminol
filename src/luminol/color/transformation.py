import colorsys
from ..core.data_types import RGB, RGBA


def _hsv_transform(r, g, b, hue_shift=0, sat_factor=1.0, bright_factor=1.0):
    """
    Apply hue, saturation, and brightness transformations
    using the HSV color space.
    """
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)

    # Apply hue shift
    if hue_shift != 0:
        h = (h + hue_shift / 360.0) % 1.0

    # Apply saturation factor
    if sat_factor != 1.0:
        s = max(0.0, min(1.0, s * sat_factor))

    # Apply brightness factor
    if bright_factor != 1.0:
        v = max(0.0, min(1.0, v * bright_factor))

    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)
    return (int(r_new * 255), int(g_new * 255), int(b_new * 255))


def _temperature(r, g, b, value=0):
    """
    Adjust color temperature (warmer/cooler).

    Args:
        r, g, b (int): RGB values (0-255)
        value (float): Temperature shift
                       (-100=cooler/blue, 0=unchanged, +100=warmer/orange)

    Returns:
        tuple: Adjusted (r, g, b) values
    """
    # Normalize value to -1 to +1
    temp = max(-100, min(100, value)) / 100.0

    if temp > 0:
        # Warmer: increase red, decrease blue
        r = int(max(0, min(255, r + (255 - r) * temp * 0.5)))
        b = int(max(0, min(255, b - b * temp * 0.3)))
    else:
        # Cooler: increase blue, decrease red
        temp = abs(temp)
        b = int(max(0, min(255, b + (255 - b) * temp * 0.5)))
        r = int(max(0, min(255, r - r * temp * 0.3)))

    return (r, g, b)


def _contrast(r, g, b, value=1.0):
    """
    Adjust contrast of RGB color.

    Args:
        r, g, b (int): RGB values (0-255)
        value (float): Contrast factor
                       (0.0=no contrast, 1.0=unchanged, 2.0+=high contrast)

    Returns:
        tuple: Adjusted (r, g, b) values
    """
    # Normalize to 0-1
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    # Apply contrast around midpoint (0.5)
    r_new = (r_norm - 0.5) * value + 0.5
    g_new = (g_norm - 0.5) * value + 0.5
    b_new = (b_norm - 0.5) * value + 0.5

    # Clamp and convert back
    r = int(max(0, min(255, r_new * 255)))
    g = int(max(0, min(255, g_new * 255)))
    b = int(max(0, min(255, b_new * 255)))

    return (r, g, b)


def _transform_color(
    rgb: RGB | RGBA,
    hue: int | None = None,
    saturation: float | None = None,
    brightness: float | None = None,
    contrast: float | None = None,
    temp: int | None = None,
    opacity: float | None = None,
) -> RGBA:
    r, g, b = rgb.r, rgb.g, rgb.b

    # Set initial alpha. If an RGBA is passed, use its alpha,
    # otherwise default to 1.0
    a = rgb.a if isinstance(rgb, RGBA) else 1.0

    # Handle HSV transformations
    hue_shift = hue if hue is not None else 0
    sat_factor = saturation if saturation is not None else 1.0
    bright_factor = brightness if brightness is not None else 1.0

    if hue_shift != 0 or sat_factor != 1.0 or bright_factor != 1.0:
        r, g, b = _hsv_transform(r, g, b, hue_shift, sat_factor, bright_factor)

    # Handle other transformations
    if contrast is not None and contrast != 1.0:
        r, g, b = _contrast(r, g, b, value=contrast)

    if temp is not None and temp != 0:
        r, g, b = _temperature(r, g, b, value=temp)

    # If opacity is explicitly passed, it overrides any existing alpha
    if opacity is not None:
        a = max(0.0, min(1.0, opacity))

    return RGBA(r, g, b, a)
