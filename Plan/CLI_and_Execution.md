# CLI and Execution Pipeline

This document covers how to run Luminol from the command line and the internal steps it takes to generate a theme.

## Command Line Interface (CLI)

```
Usage: luminol [options] image_path

Options:
  -i  --image               relative or absolute Path to the wallpaper
  -t, --theme THEME         Force theme type (light, dark). Overrides config file.
  -q, --quality LEVEL       Processing quality (fast, balanced, high).
  -v, --verbose             Enable verbose logging.
  -h, --help                Show this help message.
  --dry-run
```

**Example:** `luminol --theme dark  -i ~/Pictures/Wallpapers/my-wallpaper.png`
