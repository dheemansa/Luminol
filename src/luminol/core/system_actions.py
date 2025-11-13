import logging
import subprocess
import shlex
from pathlib import Path
from datetime import datetime
from ..exceptions.exceptions import WallpaperSetError
from ..cli.term_colors import AnsiColors
from ..utils.path import _expand_path

ERR = AnsiColors.ERROR
RESET = AnsiColors.RESET


def _run_detached_command(
    command: str, log_dir: str | Path | None, use_shell: bool = False
) -> None:
    if not command:
        logging.warning("Received an empty command.")
        return

    command_args_list: list = shlex.split(command)
    logging.info(f"Executing command: '{command}'")

    if not log_dir:
        try:
            if use_shell is False:
                subprocess.Popen(command_args_list, start_new_session=True)
            else:
                subprocess.Popen(command, shell=True, start_new_session=True)

            logging.info(f"Successfully launched '{command}' without logging.")
        except OSError as e:
            logging.error(f"Failed to launch '{command}': {e}")
        return

    try:
        expanded_log_dir = _expand_path(log_dir)

        expanded_log_dir.mkdir(parents=True, exist_ok=True)
        log_path = expanded_log_dir / f"{command_args_list[0]}.log"

        # using append mode instead of write because, 2 different reload commands might be using the same command name
        # for example, kill foo and kill bar, both are different command but them have the same command name
        # so the latter will overwrite thre previous commamdn
        log_file = open(log_path, "a")

        log_file.write(
            f"****[Date: {datetime.now().date()}][Time: {datetime.now().strftime('%H:%M:%S')}]****\n\n"
        )
        log_file.write(f"Command: {command}\n\n")
        log_file.write(f"{'*' * 50}  Logging Started  {'*' * 50}\n\n")
        if use_shell is False:
            subprocess.Popen(
                command_args_list,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        else:
            subprocess.Popen(
                command,
                shell=True,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        # TODO: Verify if closing the file handle here is robust. The Popen'd
        # child process inherits the file descriptor, but closing it in the
        # parent immediately after launch might lead to race conditions or
        # lost output on some platforms.
        log_file.close()

        logging.info(f"Successfully launched '{command}' with logging to {log_path}")
    except OSError as e:
        logging.error(f"Failed to launch '{command}': {e}")
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while trying to run '{command}': {e}"
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
    final_command = wallpaper_set_command.replace(
        "{wallpaper_path}", f"'{str(image_path)}'"
    )

    logging.debug(f"Executing wallpaper command: {final_command}")

    try:
        _run_detached_command(command=final_command, log_dir=log_dir, use_shell=False)

    except Exception as e:
        raise WallpaperSetError(f"Failed to launch wallpaper command: {e}")


def run_reload_commands(
    reload_commands: list[str],
    use_shell: bool = False,
    log_dir: str | Path | None = None,
) -> None:
    """
    Execute a list of reload commands sequentially.

    Each command is launched as a detached, fire-and-forget process.

    Args:
        reload_commands (list[str]): Commands to execute.
        use_shell (bool): If True, enables shell features (pipes, ||, etc.).
                          Avoid using with untrusted input for security reasons.
    """
    for cmd in reload_commands:
        logging.debug(f"Running reload command: {cmd}")
        # Commands are run as detached processes ("fire-and-forget") to prevent
        # blocking commands (like 'waybar') from hanging Luminol.
        try:
            if use_shell:
                _run_detached_command(command=cmd, log_dir=log_dir, use_shell=True)
            else:
                _run_detached_command(command=cmd, log_dir=log_dir, use_shell=False)
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while trying to run '{cmd}': {e}"
            )

    logging.info("All reload commands executed.")
