def _brightness(r, g, b, value=1.0):
    """
    Adjust brightness of RGB color.

    Args:
        r, g, b (int): RGB values (0-255)
        value (float): Brightness factor (0.0=black, 1.0=unchanged, 2.0+=brighter)

    Returns:
        tuple: Adjusted (r, g, b) values
    """
    r = int(max(0, min(255, r * value)))
    g = int(max(0, min(255, g * value)))
    b = int(max(0, min(255, b * value)))
    return (r, g, b)


def _saturation(r, g, b, value=1.0):
    """
    Adjust saturation of RGB color.

    Args:
        r, g, b (int): RGB values (0-255)
        value (float): Saturation factor (0.0=gray, 1.0=unchanged, 2.0+=vibrant)

    Returns:
        tuple: Adjusted (r, g, b) values
    """
    # Convert to 0-1 range
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0

    # Calculate grayscale (luminance)
    gray = 0.299 * r_norm + 0.587 * g_norm + 0.114 * b_norm

    # Interpolate between gray and original color
    r_new = gray + (r_norm - gray) * value
    g_new = gray + (g_norm - gray) * value
    b_new = gray + (b_norm - gray) * value

    # Clamp and convert back to 0-255
    r = int(max(0, min(255, r_new * 255)))
    g = int(max(0, min(255, g_new * 255)))
    b = int(max(0, min(255, b_new * 255)))

    return (r, g, b)


def _opacity(r, g, b, value=1.0):
    """
    Set opacity/alpha channel.

    Args:
        r, g, b (int): RGB values (0-255)
        value (float): Opacity (0.0=transparent, 1.0=opaque)

    Returns:
        tuple: (r, g, b, a) with alpha channel (0-255)
    """
    a = int(max(0, min(255, value * 255)))
    return (r, g, b, a)


def _hue(r, g, b, value=0):
    """
    Shift hue of RGB color.

    Args:
        r, g, b (int): RGB values (0-255)
        value (float): Hue shift in degrees (-360 to +360)

    Returns:
        tuple: Adjusted (r, g, b) values
    """
    # Convert RGB to HSV
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0

    max_c = max(r_norm, g_norm, b_norm)
    min_c = min(r_norm, g_norm, b_norm)
    diff = max_c - min_c

    # Calculate hue
    if diff == 0:
        h = 0
    elif max_c == r_norm:
        h = 60 * (((g_norm - b_norm) / diff) % 6)
    elif max_c == g_norm:
        h = 60 * (((b_norm - r_norm) / diff) + 2)
    else:
        h = 60 * (((r_norm - g_norm) / diff) + 4)

    # Calculate saturation
    s = 0 if max_c == 0 else diff / max_c

    # Calculate value
    v = max_c

    # Apply hue shift
    h = (h + value) % 360

    # Convert back to RGB
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r_new, g_new, b_new = c, x, 0
    elif 60 <= h < 120:
        r_new, g_new, b_new = x, c, 0
    elif 120 <= h < 180:
        r_new, g_new, b_new = 0, c, x
    elif 180 <= h < 240:
        r_new, g_new, b_new = 0, x, c
    elif 240 <= h < 300:
        r_new, g_new, b_new = x, 0, c
    else:
        r_new, g_new, b_new = c, 0, x

    r = int((r_new + m) * 255)
    g = int((g_new + m) * 255)
    b = int((b_new + m) * 255)

    return (r, g, b)


def _temperature(r, g, b, value=0):
    """
    Adjust color temperature (warmer/cooler).

    Args:
        r, g, b (int): RGB values (0-255)
        value (float): Temperature shift (-100=cooler/blue, 0=unchanged, +100=warmer/orange)

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
        value (float): Contrast factor (0.0=no contrast, 1.0=unchanged, 2.0+=high contrast)

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


def transform_color(
    rgb: tuple,
    hue: int = 0,
    saturation: float = 1.0,
    brightness: float = 1.0,
    contrast: float = 1.0,
    temp: int | None = None,
    opacity: float = 1.0,
) -> tuple[int, int, int, float]:
    r, g, b = rgb
    a = 1.0

    if hue != 0:
        r, g, b = _hue(r, g, b, value=hue)

    if saturation != 1.0:
        r, g, b = _saturation(r, g, b, value=saturation)

    if brightness != 1.0:
        r, g, b = _brightness(r, g, b, value=brightness)

    if contrast != 1.0:
        r, g, b = _contrast(r, g, b, value=contrast)

    if temp is not None:
        r, g, b = _temperature(r, g, b, value=temp)

    if opacity != 1.0:
        a = opacity

    return (r, g, b, a)


# Example usage
if __name__ == "__main__":
    # Test color: orange-ish (255, 140, 70)
    test_color = (255, 140, 70)
    print(f"Original color: RGB{test_color}")
    print()

    # Brightness
    print("BRIGHTNESS:")
    print(f"  20% darker (0.8): RGB{_brightness(*test_color, 0.8)}")
    print(f"  30% brighter (1.3): RGB{_brightness(*test_color, 1.3)}")
    print()

    # Saturation
    print("SATURATION:")
    print(f"  More muted (0.4): RGB{_saturation(*test_color, 0.4)}")
    print(f"  More vibrant (1.5): RGB{_saturation(*test_color, 1.5)}")
    print()

    # Opacity
    print("OPACITY:")
    r, g, b, a = _opacity(*test_color, 0.8)
    print(f"  20% transparent (0.8): RGBA{r, g, b, a}")
    r, g, b, a = _opacity(*test_color, 0.3)
    print(f"  70% transparent (0.3): RGBA{r, g, b, a}")
    print()

    # Hue
    print("HUE:")
    print(f"  Shift +30°: RGB{_hue(*test_color, 30)}")
    print(f"  Shift -45°: RGB{_hue(*test_color, -45)}")
    print(f"  Opposite (180°): RGB{_hue(*test_color, 180)}")
    print()

    # Temperature
    print("TEMPERATURE:")
    print(f"  Warmer (+20): RGB{_temperature(*test_color, 20)}")
    print(f"  Cooler (-15): RGB{_temperature(*test_color, -15)}")
    print()

    # Contrast
    print("CONTRAST:")
    print(f"  Higher (1.4): RGB{_contrast(*test_color, 1.4)}")
    print(f"  Lower (0.7): RGB{_contrast(*test_color, 0.7)}")
