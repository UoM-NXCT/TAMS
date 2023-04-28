"""Library index."""
from pathlib import Path

from client import settings


def get_relative_path(prj_id: str | int | Path, scan_id: str | int | Path) -> Path:
    """Get the relative path to a scan in the library.

    :param prj_id: project ID
    :param scan_id: scan ID
    :return: relative path to scan
    """
    return Path(str(prj_id)) / Path(str(scan_id))


def local_path(relative_path: Path) -> Path:
    """Get the local path to a scan in the library.

    :param relative_path: relative path
    :return: local path
    """
    return Path(settings.get_lib("local")) / relative_path
