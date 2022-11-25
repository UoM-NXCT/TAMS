"""
Base settings.
"""

from pathlib import Path

from client.utils.toml import load_toml

TAMS_DIR: Path = Path(__file__).parents[1]

general: Path = TAMS_DIR / "settings" / "general.toml"
database: Path = TAMS_DIR / "settings" / "database.toml"
placeholder_image: Path = TAMS_DIR / "resources" / "404.png"
logo: Path = TAMS_DIR / "resources" / "tams.png"
splash: Path = TAMS_DIR / "resources" / "splash.png"


def get_lib(lib_title: str) -> str:
    """Get the current library to present to the user."""

    return str(load_toml(general)["storage"][f"{lib_title}_library"])


def get_perm_dir_name() -> str:
    """Get the name of the permanent storage directory."""

    return str(load_toml(general)["structure"]["perm_dir_name"])
