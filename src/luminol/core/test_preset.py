from .data_types import RGB

TEST_PRESET: dict[str, RGB] = {
    # UI Semantic Colors (13)
    "bg-primary": RGB(30, 30, 46),
    "bg-secondary": RGB(49, 50, 68),
    "bg-tertiary": RGB(69, 71, 90),
    "text-primary": RGB(205, 214, 244),
    "text-secondary": RGB(186, 194, 222),
    "text-tertiary": RGB(128, 128, 128),
    "accent-primary": RGB(138, 244, 218),
    "accent-secondary": RGB(243, 139, 168),
    "error-color": RGB(243, 139, 168),
    "warning-color": RGB(249, 226, 175),
    "success-color": RGB(166, 227, 161),
    "border-active": RGB(205, 214, 244),
    "border-inactive": RGB(49, 50, 68),

    # ANSI Colors (16)
    "ansi-0": RGB(0, 0, 0),          # Black
    "ansi-1": RGB(255, 50, 50),      # Red
    "ansi-2": RGB(50, 255, 50),      # Green
    "ansi-3": RGB(255, 255, 50),     # Yellow
    "ansi-4": RGB(80, 120, 255),     # Blue
    "ansi-5": RGB(255, 50, 255),     # Magenta
    "ansi-6": RGB(50, 255, 255),     # Cyan
    "ansi-7": RGB(224, 224, 224),    # White
    "ansi-8": RGB(128, 128, 128),    # Bright Black
    "ansi-9": RGB(255, 100, 100),    # Bright Red
    "ansi-10": RGB(100, 255, 100),   # Bright Green
    "ansi-11": RGB(255, 255, 100),   # Bright Yellow
    "ansi-12": RGB(130, 150, 255),   # Bright Blue
    "ansi-13": RGB(255, 100, 255),   # Bright Magenta
    "ansi-14": RGB(100, 255, 255),   # Bright Cyan
    "ansi-15": RGB(255, 255, 255),   # Bright White
}
