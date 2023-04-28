"""Base settings."""
from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

from client.utils import log
from client.utils.toml import create_toml, load_toml

if TYPE_CHECKING:
    from collections.abc import Callable

TAMS_DIR: Path = Path(__file__).parents[1]

general: Path = TAMS_DIR / "settings" / "general.toml"
database: Path = TAMS_DIR / "settings" / "database.toml"
log_file: Path = TAMS_DIR / "settings" / "file.log"
placeholder_image: Path = TAMS_DIR / "resources" / "404.png"
logo: Path = TAMS_DIR / "resources" / "tams.png"
splash: Path = TAMS_DIR / "resources" / "splash.png"

default_general_settings: dict[str, Any] = {
    "storage": {
        "local_library": "",
        "permanent_library": "",
    },
    "structure": {
        "perm_dir_name": "raw",
    },
}

# Type variables for the access_settings decorator
P = ParamSpec("P")
R = TypeVar("R")


def access_settings(func: Callable[P, R]) -> Callable[P, R]:
    """Decorate functions that access settings files."""

    @wraps(func)
    def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> R:
        """Attempt to execute the sql command, and handle any exceptions."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            # Settings file does not exist
            log.logger(__name__).warning("Settings file does not exist, creating it.")
            create_toml(general, default_general_settings)
            return func(*args, **kwargs)

    return wrapper


@access_settings
def get_lib(lib_title: str) -> str:
    """Get the current library to present to the user."""
    return str(load_toml(general)["storage"][f"{lib_title}_library"])


@access_settings
def get_perm_dir_name() -> str:
    """Get the name of the permanent storage directory."""
    return str(load_toml(general)["structure"]["perm_dir_name"])
