from typing import Optional


def rgba_to_hex(r: int, g: int, b: int, a: Optional[float] = None):
    """
    Convert RGB/RGBA color values to hexadecimal color code.

    Args:
        r (int): Red value (0-255)
        g (int): Green value (0-255)
        b (int): Blue value (0-255)
        a (float, optional): Alpha/opacity normalized value (0-1). If None, returns 6-digit hex.

    Returns:
        str: Hexadecimal color code
             - 6-digit if a is None (e.g., '#FF6432')
             - 8-digit if a is provided (e.g., '#FF6432AA')
    """

    # NOTE: i dont think this is required
    # # Ensure values are within valid range (0-255)
    # r = max(0, min(255, r))
    # g = max(0, min(255, g))
    # b = max(0, min(255, b))

    # Return 6-digit hex if alpha is not provided
    if a is None:
        return f"#{r:02X}{g:02X}{b:02X}"

    # Clamp alpha to 0–1, then scale to 0–255
    a = max(0, min(255, round(a * 255)))

    # Return 8-digit hex if alpha is provided
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


# NOTE: might need to consider options for color-format rgba(8-bit alpha) and rgba(normalized alpha)
