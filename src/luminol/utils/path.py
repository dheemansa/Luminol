import os
from pathlib import Path
import logging
import shutil
from typing import Optional


def _expand_path(path_str: str) -> Path:
    """Expand ~, ~user, and environment variables."""
    # Order: expanduser first, then expandvars
    expanded = os.path.expanduser(path_str)
    expanded = os.path.expandvars(expanded)
    return Path(expanded)


def _home_dir() -> Path:
    # FIXME this is the wrong implemention, we are trying to get XDG Config home for Home path
    # FIXME fix this by using hard coded logic in the LuminolPath class instead of using a function to get the home path

    # TODO: Remove this function and implement XDG Base Directory logic directly in LuminolPath
    # - luminol_path: check XDG_CONFIG_HOME/luminol, fallback to ~/.config/luminol
    # - cache_path: check XDG_CACHE_HOME/luminol, fallback to ~/.cache/luminol
    xdg_config_home_env = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home_env:
        xdg_config_home = Path(xdg_config_home_env)
        if xdg_config_home.is_dir():
            logging.debug(f"Using {xdg_config_home}")
            return xdg_config_home
        logging.debug(f"{xdg_config_home} not found")

    home_path = Path.home()
    if home_path.is_dir():
        logging.debug(f"Using {home_path}")
        return home_path

    raise FileNotFoundError("$XDG_CONFIG_HOME or $HOME: no such directory exists")


class LuminolPath:
    # NOTE all the path are not computed at class initialisation because it will throw an error if an path is not valid
    # NOTE i want it to raise an error if a required path is invalid, so i have tried to implement lazy loding of properties
    def __init__(
        self,
        config_dir: Optional[str] = None,
        cache_dir: Optional[str] = None,
        config_file_path: Optional[str] = None,
    ) -> None:
        self._config_dir: Path | None = None
        self._cache_dir: Path | None = None
        self._config_file_path: Path | None = None

        if config_dir is not None:
            self._config_dir: Path = _expand_path(config_dir)
            if not self._config_dir.exists():
                logging.error("No such directory exists:", self._config_dir)
                raise FileNotFoundError(f"No such directory exists: {self._config_dir}")

        if cache_dir is not None:
            self._cache_dir: Path = _expand_path(cache_dir)
            if not self._cache_dir.exists():
                logging.error("No such directory exists:", self._cache_dir)
                raise FileNotFoundError(f"No such directory exists: {self._cache_dir}")

        if config_file_path is not None:
            self._config_file_path: Path = _expand_path(config_file_path)
            if not self._config_file_path.exists():
                logging.error("No such file exists:", self._config_file_path)
                raise FileNotFoundError(
                    f"No such file exists: {self._config_file_path}"
                )

    def luminol_path(self) -> Path:
        if self._config_dir is not None:
            return self._config_dir

        ## function is terminated if a custom path is given
        ## the rest of the logic only executes if _config_dir is set to None

        """Return the path to luminol directory, checking XDG then ~/.config."""
        # check for xdg home config
        xdg_config_home_env = os.getenv("XDG_CONFIG_HOME")
        if xdg_config_home_env:
            xdg_config_home = Path(xdg_config_home_env)
            if xdg_config_home.is_dir():
                logging.debug(f"Using {xdg_config_home}")
                luminol_path = xdg_config_home / "luminol"
                if luminol_path.is_dir():
                    return luminol_path
                else:
                    logging.debug(f"No such file exists: {luminol_path}")

        logging.debug("$XDG_CONFIG_HOME/luminol not found")

        home_path = Path.home()
        if home_path.is_dir():
            luminol_path = home_path / ".config" / "luminol"
            if luminol_path.is_dir():
                return luminol_path

        raise FileNotFoundError(
            "$XDG_CONFIG_HOME/luminol or $HOME/.config/luminol: no such directory exists"
        )

    @property
    def cache_path(self) -> Path:
        if self._cache_dir is not None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            return self._cache_dir

        ## function is terminated if a custom path is given
        ## the rest of the logic only executes if _config_dir is set to None
        xdg_cache_home_env = os.getenv("XDG_CONFIG_HOME")
        if xdg_cache_home_env:
            xdg_cache_home = Path(xdg_cache_home_env)
            if xdg_cache_home.is_dir():
                luminol_cache_dir = xdg_cache_home / "luminol"
                luminol_cache_dir.mkdir(parents=True, exist_ok=True)
                return luminol_cache_dir

        home_cache_path = Path.home() / ".cache"
        luminol_cache_dir = home_cache_path / "luminol"
        luminol_cache_dir.mkdir(parents=True, exist_ok=True)

        return luminol_cache_dir

    def clear_cache(self) -> None:
        try:
            shutil.rmtree(str(self.cache_path))
        except Exception as e:
            logging.critical("Unable to clear cache.", e)

    @property
    def template_dir(self) -> Path:
        template_dir = self.luminol_path() / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        return template_dir

    @property
    def config_file_path(self) -> Path:
        if self._config_file_path is not None:
            return self._config_file_path

        config_file = self.luminol_path() / "config.toml"
        if config_file.is_file():
            return config_file
        raise FileNotFoundError(
            "No config.toml found in $XDG_CONFIG_HOME/luminol or ~/.config/luminol"
        )

    # TODO make function with argument dir_name,file_name,contents and store it in cache
    # TODO make function to copy files saved in cache to the specified location


# Example use
# print(LuminolPath.template_dir)
# print(LuminolPath.config)
# print(LuminolPath.cache_dir)
