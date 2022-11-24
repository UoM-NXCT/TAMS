"""
Base settings.
"""

from pathlib import Path

from client.utils.toml import get_value_from_toml

TAMS_DIR: Path = Path(__file__).parents[1]

general: Path = TAMS_DIR / "settings" / "general.toml"
database: Path = TAMS_DIR / "settings" / "database.toml"
placeholder_image: Path = TAMS_DIR / "resources" / "404.png"
logo: Path = TAMS_DIR / "resources" / "tams.png"
splash: Path = TAMS_DIR / "resources" / "splash.png"
perm_storage_dir_name = "raw"


def get_lib(lib_title: str) -> str | None:
    """Get the current library to present to the user."""

    current_lib = str(get_value_from_toml(general, "storage", f"{lib_title}_library"))
    if current_lib:
        return current_lib
    return None
