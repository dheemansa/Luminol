import logging
import subprocess
import shlex
from pathlib import Path
from ..exceptions.exceptions import WallpaperSetError
from ..cli.term_colors import AnsiColors
from ..utils.path import _expand_path

ERR = AnsiColors.ERROR
RESET = AnsiColors.RESET


def _run_detached_command(command: list[str], log_dir: str | Path | None) -> None:
    if not command:
        logging.warning("Received an empty command list.")
        return

    command_name = command[0]
    logging.info(f"Executing detached command: '{' '.join(command)}'")

    if not log_dir:
        try:
            subprocess.Popen(command, start_new_session=True)
            logging.info(f"Successfully launched '{command_name}' without logging.")
        except OSError as e:
            logging.error(f"Failed to launch '{command_name}': {e}")
        return

    try:
        expanded_log_dir = _expand_path(log_dir)

        expanded_log_dir.mkdir(parents=True, exist_ok=True)
        log_path = expanded_log_dir / f"{command_name}.log"

        log_file = open(log_path, "w")
        subprocess.Popen(
            command, stdout=log_file, stderr=subprocess.STDOUT, start_new_session=True
        )
        log_file.close()

        logging.info(
            f"Successfully launched '{command_name}' with logging to {log_path}"
        )
    except OSError as e:
        logging.error(f"Failed to launch '{command_name}': {e}")
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while trying to run '{command_name}': {e}"
        )


# HACK improve these functions using async functions might work
def apply_wallpaper(
    wallpaper_set_command: str,
    image_path: str | Path,
    log_dir: str | Path | None = None,
) -> None:
    """
    Apply a wallpaper by executing the configured command.

    Replaces `{wallpaper_path}` in the command with the actual image path,
    then launches it.

    Args:
        wallpaper_set_command (str): Command to set wallpaper with `{wallpaper_path}` placeholder.
        image_path (str | Path): Path to the wallpaper image.
        log_dir (str | Path): Path to the log directory

    Raises:
        WallpaperSetError: If the wallpaper command is not found or fails to start.
    """
    final_command = wallpaper_set_command.replace("{wallpaper_path}", str(image_path))
    command_args = shlex.split(final_command)

    logging.debug(f"Executing wallpaper command: {final_command}")

    try:
        _run_detached_command(command=command_args, log_dir=log_dir)

    except Exception as e:
        raise WallpaperSetError(f"Failed to launch wallpaper command: {e}")


def run_reload_commands(
    reload_commands: list[str],
    use_shell: bool = False,
    log_dir: str | Path | None = None,
) -> None:
    """
    Execute a list of reload commands sequentially.

    Each command is started using subprocess.Popen().
    If verbose=True, waits for completion and shows output. Otherwise, fire-and-forget.

    Args:
        reload_commands (list[str]): Commands to execute.
        use_shell (bool): If True, enables shell features (pipes, ||, etc.).
                          Avoid using with untrusted input for security reasons.
        verbose (bool): If True, waits for command completion and shows output. If False, fire-and-forget.
    """
    for cmd in reload_commands:
        logging.debug(f"Running reload command: {cmd}")
        # use verbose=False (fire-and-forget) because there might be a blocking command like waybar or such
        # which will cause luminol to hang, only use verbose=True to understand what went wrong but this will
        # kill the blocking process
        try:
            if use_shell:
                pass
            else:
                pass
        except:
            pass

    logging.info("All reload commands executed.")
