# Template System

For applications that use complex configuration files, Luminol supports a template system. Instead of generating a simple list of color variables, Luminol can take a template file, substitute placeholders with generated colors, and write the result to the application's configuration path.

## Template-Based Configuration

To enable template mode for an application, you must specify the `template` key in its configuration.

```toml
[dunst]
enabled = true
color_format = "hex6"
file = "~/.config/dunst/dunstrc" # Final output path
syntax = "{placeholder}" # Must be set to {placeholder} for templates
template = "dunst.template" # Name of the template file

# Mappings for the placeholders inside the template file
[dunst.placeholders]
frame_color = "accent-primary"
bg_low = "bg-primary"
fg_low = "text-primary"
bg_crit = ["error-color", "brightness=0.8"]
fg_crit = "text-primary"
```

### How Placeholders Work

When `syntax` is set to `"{placeholder}"`, Luminol switches to its template engine. It reads the `[app.placeholders]` table and uses each key to create a placeholder.

1.  A key in the `[app.placeholders]` table (e.g., `frame_color`) is turned into a placeholder by adding curly braces (e.g., `{frame_color}`).
2.  Luminol then reads the specified `template` file.
3.  It finds and replaces all occurrences of that placeholder with the final color value derived from the mapping (e.g., `accent-primary`).
4.  The resulting content is written to the output `file`.

This allows for the generation of complex configuration files where colors might be needed in very specific places.

## Template File Location

All template files **must** be located in the `$XDG_CONFIG_HOME/luminol/templates/` directory (e.g., `~/.config/luminol/templates/`). You only need to provide the filename in the `template` key.

## Template Example (`dunst.template`)

This is a simplified example of what a `dunst.template` file might contain. Luminol will read this file, replace the placeholders like `{frame_color}` with the colors defined in the `[dunst.placeholders]` table, and write the final output to the `file` path (`~/.config/dunst/dunstrc`).

```ini
[global]
frame_width = 2
frame_color = "{frame_color}"
font = JetBrainsMono Nerd Font 13

[urgency_low]
background = "{bg_low}"
foreground = "{fg_low}"
timeout = 10

[urgency_critical]
background = "{bg_crit}"
foreground = "{fg_crit}"
timeout = 0
```
