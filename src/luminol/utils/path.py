import os
from pathlib import Path
import logging
import shutil
from datetime import datetime, timedelta


def _expand_path(path_str: str | Path) -> Path:
    """Expand ~, ~user, and environment variables."""
    expanded = os.path.expanduser(str(path_str))
    expanded = os.path.expandvars(expanded)
    return Path(expanded)


def _validate_path(path: Path, path_type: str = "directory") -> Path:
    """Validate that a path exists and is of the correct type."""
    if not path.exists():
        raise FileNotFoundError(f"No such {path_type} exists: {path}")

    if path_type == "directory" and not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    if path_type == "file" and not path.is_file():
        raise FileNotFoundError(f"Path is not a file: {path}")

    return path


def get_luminol_dir(custom_config_dir: str | None = None) -> Path:
    """
    Return the path to luminol directory.

    Priority order:
    1. Custom config directory (if provided)
    2. $XDG_CONFIG_HOME/luminol
    3. ~/.config/luminol

    Args:
        custom_config_dir: Optional custom config directory path

    Returns:
        Path to the luminol configuration directory

    Raises:
        FileNotFoundError: If no valid luminol directory is found
    """
    # Use custom directory if provided
    if custom_config_dir is not None:
        custom_path = _expand_path(custom_config_dir)
        return _validate_path(custom_path, "directory")

    # Check XDG_CONFIG_HOME
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        xdg_path = Path(xdg_config_home)
        if xdg_path.is_dir():
            luminol_path = xdg_path / "luminol"
            if luminol_path.is_dir():
                logging.debug("Using XDG config: %s", luminol_path)
                return luminol_path

    logging.debug("$XDG_CONFIG_HOME/luminol not found")

    # Fallback to ~/.config/luminol
    home_config = Path.home() / ".config" / "luminol"
    if home_config.is_dir():
        logging.debug("Using home config: %s", home_config)
        return home_config

    raise FileNotFoundError(
        "No luminol directory found. Searched:\n"
        "  - $XDG_CONFIG_HOME/luminol\n"
        "  - ~/.config/luminol"
    )


def get_cache_dir(custom_cache_dir: str | None = None) -> Path:
    """
    Return the path to luminol cache directory, creating it if needed.

    Priority order:
    1. Custom cache directory (if provided)
    2. $XDG_CACHE_HOME/luminol
    3. ~/.cache/luminol

    Args:
        custom_cache_dir: Optional custom cache directory path

    Returns:
        Path to the luminol cache directory
    """
    # Use custom directory if provided
    if custom_cache_dir is not None:
        cache_path = _expand_path(custom_cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path

    # Check XDG_CACHE_HOME
    xdg_cache_home = os.getenv("XDG_CACHE_HOME")
    if xdg_cache_home:
        xdg_path = Path(xdg_cache_home)
        if xdg_path.is_dir():
            cache_path = xdg_path / "luminol"
            cache_path.mkdir(parents=True, exist_ok=True)
            return cache_path

    # Fallback to ~/.cache/luminol
    cache_path = Path.home() / ".cache" / "luminol"
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def get_base_log_dir(custom_log_dir: str | None = None) -> Path:
    """
    Return the path to the base log directory, creating it if needed.

    Priority order for the base directory:
    1. Custom log directory (if provided)
    2. $XDG_STATE_HOME/luminol
    3. ~/.local/state/luminol

    Args:
        custom_log_dir: Optional custom base log directory path

    Returns:
        Path to the base log directory.
    """
    if custom_log_dir is not None:
        base_log_path = _expand_path(custom_log_dir)

    else:
        # Check XDG_STATE_HOME
        xdg_state_home = os.getenv("XDG_STATE_HOME")
        if xdg_state_home:
            base_log_path = _expand_path(xdg_state_home) / "luminol" / "logs"
        else:
            # Fallback to ~/.local/state/luminol
            base_log_path = Path.home() / ".local" / "state" / "luminol" / "logs"

    return base_log_path


def get_log_dir(custom_log_dir: str | None = None) -> Path:
    """
    Return the path to the log directory for the current run, creating it if needed.

    The path will be timestamped for each run, e.g., .../luminol/logs/YYYY-MM-DD_HH-MM-SS.

    Priority order for the base directory:
    1. Custom log directory (if provided)
    2. $XDG_STATE_HOME/luminol
    3. ~/.local/state/luminol

    Args:
        custom_log_dir: Optional custom base log directory path

    Returns:
        Path to the timestamped log directory for the current run.
    """
    # Use custom directory if provided
    if custom_log_dir is not None:
        base_log_path = _expand_path(custom_log_dir)
    else:
        base_log_path = get_base_log_dir()

    # A new timestamped directory is created for each run. This is to isolate
    # log outputs and prevent detached, long-running processes from a previous
    # run from writing to the same log files as processes from the current run.
    # The YYYY-MM-DD_HH-MM-SS format also ensures chronological sorting.
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = base_log_path / "logs" / timestamp
    log_path.mkdir(parents=True, exist_ok=True)
    logging.debug("Using log directory: %s", log_path)
    return log_path


def clear_old_logs(days: int = 7) -> None:
    """
    Remove log directories older than a specified number of days.

    Args:
        days (int): The maximum age of logs in days to keep.
    """
    base_log_path = get_base_log_dir()

    if not base_log_path.is_dir():
        logging.debug("Log directory base does not exist, skipping cleanup.")
        return

    logging.debug("Checking for logs older than %s days in %s", days, base_log_path)
    now = datetime.now()
    cutoff = timedelta(days=days)

    for log_dir in base_log_path.iterdir():
        if not log_dir.is_dir():
            continue

        try:
            log_time = datetime.strptime(log_dir.name, "%Y-%m-%d_%H-%M-%S")
            if now - log_time > cutoff:
                logging.info("Removing old log directory: %s", log_dir)
                shutil.rmtree(log_dir)
        except ValueError:
            # Ignore directories that don't match the timestamp format
            logging.debug(
                "Skipping cleanup for non-timestamped directory: %s", log_dir.name
            )
        except Exception as e:
            logging.error("Failed to remove directory %s: %s", log_dir, e)


def clear_directory(dir_path: str | Path, preserve_dir: bool = True) -> None:
    """
    Clear a directory by removing all its contents.

    Args:
        dir_path: Path to the directory to clear
        preserve_dir: If True, only the contents are deleted (default: True)

    Raises:
        Exception: If unable to clear the directory
    """

    path = Path(dir_path)
    try:
        if not path.exists():
            # when path not found
            logging.debug("Skipped (doesn't exist): %s", path)
            return

        if preserve_dir:
            for item in path.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

            logging.debug("Cleared contents of: %s", path)
            return

        # when preserve_dir is false
        shutil.rmtree(path)
        logging.debug("Removed: %s", path)
        return

    except PermissionError as e:
        logging.error("Permission denied while clearing '%s': %s", path, e)
        raise
    except Exception as e:
        logging.error("Failed to clear '%s': %s", path, e)
        raise


def _is_file_name(path: str):
    return Path(path).parent == Path(".")
