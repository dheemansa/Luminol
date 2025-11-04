"""
Module for executing detached system commands.
"""
import subprocess
import os
from pathlib import Path
from typing import List
import logging

# Configure logging
logger = logging.getLogger(__name__)

def run_detached_command(command: List[str], log_dir: str | None) -> None:
    """
    Executes a command in the background and detaches it from the script's lifecycle.
    This is a non-blocking, "fire and forget" call suitable for starting daemons,
    setting wallpapers, or running other background tasks.

    Args:
        command: The command to execute, as a list of strings (e.g., ["swaybg", "-i", "file.jpg"]).
        log_dir: The directory to store logs in. If None, logging is disabled.
    """
    if not command:
        logger.warning("Received an empty command list.")
        return

    command_name = command[0]
    logger.info(f"Executing detached command: '{' '.join(command)}'")

    # If logging is disabled, execute without redirection and detach.
    if not log_dir:
        try:
            subprocess.Popen(command, start_new_session=True)
            logger.info(f"Successfully launched '{command_name}' without logging.")
        except OSError as e:
            logger.error(f"Failed to launch '{command_name}': {e}")
        return

    # --- Safe Logged Execution ---
    try:
        # 1. Prepare the log file path and ensure the directory exists.
        expanded_log_dir = Path(os.path.expanduser(log_dir))
        os.makedirs(expanded_log_dir, exist_ok=True)
        log_path = expanded_log_dir / f"{command_name}.log"

        # 2. Open the log file to be used for stdout and stderr.
        #    We use 'a' to append, which is useful for restarts.
        #    In this specific Popen case, we do NOT close the file handle in the
        #    parent process. The child process takes ownership of the handle,
        #    and the OS will close it when the child terminates.
        log_file = open(log_path, 'a')

        # 3. Execute the command safely.
        #    - `command` is a list, so no shell injection is possible.
        #    - `stdout` and `stderr` are redirected to our file handle.
        #    - `start_new_session=True` detaches the process so it keeps running.
        subprocess.Popen(
            command,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        logger.info(f"Successfully launched '{command_name}' with logging to {log_path}")

    except OSError as e:
        logger.error(f"Failed to launch '{command_name}' with logging: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while trying to run '{command_name}': {e}")