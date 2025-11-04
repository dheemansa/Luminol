def luma(r: int, g: int, b: int, quality: str = "high") -> float:
    """
    Calculate perceived brightness (luma) from RGB values.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
        quality: "high" (default) or "fast"

    Returns:
        float: Luma value from 0-255

    Raises:
        ValueError: If quality is not "high" or "fast"
    """

    if quality == "fast":
        # Fast approximation using Rec. 709 coefficients
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    elif quality == "high":
        # High-quality with gamma correction
        def to_linear(c):
            c = c / 255.0
            if c <= 0.04045:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        r_lin = to_linear(r)
        g_lin = to_linear(g)
        b_lin = to_linear(b)

        # Apply coefficients in linear space
        luma_linear = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
        return luma_linear * 255.0

    else:
        raise ValueError('Quality must be "high" or "fast"')


def contrast_ratio(luma1: float, luma2: float) -> float:
    """
    Calculate WCAG contrast ratio between two luma values (0-255 scale).

    Formula: (L1 + 0.05) / (L2 + 0.05) where L1 > L2
    Luma values should be normalized to 0-1 range.
    """
    # Normalize to 0-1 range (relative luminance)
    L1 = max(luma1, luma2) / 255.0
    L2 = min(luma1, luma2) / 255.0

    return (L1 + 0.05) / (L2 + 0.05)
