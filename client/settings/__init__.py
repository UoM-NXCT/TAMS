"""
Base settings.
"""

from pathlib import Path

TAMS_DIR: Path = Path(__file__).parents[1]

general: Path = TAMS_DIR / "settings" / "general.toml"
database: Path = TAMS_DIR / "settings" / "database.toml"
placeholder_image: Path = TAMS_DIR / "resources" / "404.png"
logo: Path = TAMS_DIR / "resources" / "tams.png"
splash: Path = TAMS_DIR / "resources" / "splash.png"
perm_storage_dir_name = "raw"
