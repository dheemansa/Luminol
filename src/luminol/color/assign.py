from ..color.luma import luma


def decide_theme(color_data: dict[tuple[int, int, int], dict[str, float]]) -> str:
    """
    Decide whether a palette suggests a light or dark theme.

    Args:
        color_data: dict mapping RGB tuples to dict with "coverage" and "luma" keys

    Returns:
        "light" or "dark"
    """

    THEME_THRESHOLD = 80

    # Weighted luma calculation
    weighted_luma = sum(data["luma"] * data["coverage"] for data in color_data.values())

    print(f"Weighted luma: {weighted_luma:.2f}")

    return "light" if weighted_luma > THEME_THRESHOLD else "dark"


def assign_color(raw_rgb_color: dict[tuple, float], theme_type: str = "auto"):
    THEME_THRESHOLD = 128
