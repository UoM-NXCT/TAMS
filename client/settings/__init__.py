from pathlib import Path

TAMS_DIR: Path = Path(__file__).parents[1]

general: Path = TAMS_DIR / "settings" / "general.toml"
database: Path = TAMS_DIR / "settings" / "database.toml"
