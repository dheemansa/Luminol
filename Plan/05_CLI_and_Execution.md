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
```

**Example:**
`luminol --theme dark  ~/Pictures/Wallpapers/my-wallpaper.png`

## Execution Pipeline

When you run `luminol`, it performs the following steps:

1.  **Load Config**: Reads and validates the master `config.toml` file.
2.  **Execute Wallpaper Command**: If `wallpaper-command` is defined in the `[global]` section, it is executed first.
3.  **Extract Colors**: Uses the color extraction algorithm to get a palette from the source image.
4.  **Generate Semantic Palette**: Assigns roles (`bg-primary`, `text-primary`, etc.) to the extracted colors.
5.  **Process Applications**: For each enabled application in the config file:
    a.  **Check Mode**: Determines whether to use the default (full palette) or remap (custom) mode.
    b.  **Apply Transformations**: If in remap mode, applies any color transformations (brightness, opacity, etc.).
    c.  **Generate Output**: Creates the final color file, either by substituting placeholders in a `template` or by formatting variables with the `syntax` key.
    d.  **Write File**: Writes the generated content to the specified `file` path.
6.  **Execute Reload Commands**: After all files are written, runs the `reload-commands` specified in the `[global]` section of the config.
