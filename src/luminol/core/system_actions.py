import logging
from typing import Optional
import subprocess
import shlex
from pathlib import Path
from ..exceptions.exceptions import WallpaperSetError
from ..cli.term_colors import AnsiColors

ERR = AnsiColors.ERROR
RESET = AnsiColors.RESET

# COMMAND EXECUTIONS


def apply_wallpaper(wallpaper_set_command: str, image_path: str | Path = "") -> None:
    """
    Apply a wallpaper by running a system command.

    Replaces the `{wallpaper_path}` placeholder with the given image path
    and executes the command using subprocess without a shell.

    Note:
        Shell features like pipes (|), redirects (> <), or env variables will NOT work, as shell=True is not used.

    Args:
        wallpaper_set_command (str): Command to set wallpaper, optionally with `{wallpaper_path}` placeholder.
        image_path (str | Path): Path to the wallpaper image.

    Raises:
        WallpaperSetError: If the command fails, is not found, or another error occurs.

    Examples:
        With placeholder:
            wallpaper_set_command = "swww img {wallpaper_path}"
            image_path = "/home/user/Pictures/wallpaper.png"
            apply_wallpaper(wallpaper_set_command, image_path)
            # Executes: swww img /home/user/Pictures/wallpaper.png

        Without placeholder:
            wallpaper_set_command = "swww img /home/user/Pictures/wallpaper.png"
            apply_wallpaper(wallpaper_set_command, image_path)
    """

    # replace the placeholder in config
    final_command = wallpaper_set_command.replace("{wallpaper_path}", str(image_path))
    command_args: list = shlex.split(final_command)

    try:
        logging.debug(f"Executing '{final_command}' for wallpaper")
        command_output = subprocess.run(
            command_args, capture_output=True, text=True, check=False
        )

        if command_output.returncode != 0:
            raise WallpaperSetError(
                f"Error occured while executing command: '{ERR}{final_command}{RESET}'"
                f"\n{command_output.stderr}"
            )

    except FileNotFoundError:
        raise WallpaperSetError(
            f"Command not found: '{ERR}{command_args[0]}{RESET}' for applying wallpaper"
        )

    except Exception as e:
        raise WallpaperSetError(
            f"Unexpected error occured while executing wallpaper command: \n{e}"
        )

    if command_output.stdout:
        logging.info(command_output.stdout)
    logging.info(f"Wallpaper Applied Successfully")


def run_reload_commands(reload_commands: list[str]) -> None:
    """
    Executes a list configured reload commands sequentially.

    Example:
        reload_commands: list = ["command1", "command2 --arg1 --arg2"]
    """
    for cmd in reload_commands:
        logging.debug(f"Running reload command: {cmd}")
        args = shlex.split(cmd)
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                logging.warning(f"Reload command failed ({cmd})\n{result.stderr}")
            elif result.stdout:
                logging.debug(result.stdout)

        except FileNotFoundError:
            logging.error(f"Command not found: {args[0]}")

        except Exception as e:
            logging.error(f"Unexpected error running '{cmd}': {e}")

    logging.info("All reload commands executed.")


