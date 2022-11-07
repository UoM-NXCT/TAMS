"""
Library operations for saving data.
"""

import logging
from pathlib import Path

from client.file_transfer.file_operations import create_dir_if_missing, find_and_move


def save_to_local(local: Path, permanent: Path, project_id: int, *scan_ids) -> None:
    """Save data to local library.

    :param local: local library directory
    :param permanent: permanent library directory
    :param project_id: project ID
    :param scan_ids: scan IDs
    """

    # Check if libraries exist
    if not local.exists():
        raise ValueError(f"Local library directory {local} does not exist.")
    if not permanent.exists():
        raise ValueError(f"Permanent library directory {permanent} does not exist.")

    # Create if library directories are actually directories
    if not local.is_dir():
        raise ValueError(f"Local library directory {local} is not a directory.")
    if not permanent.is_dir():
        raise ValueError(f"Permanent library directory {permanent} is not a directory.")

    # Check project exists in permanent library
    permanent_storage_dir: Path = permanent / str(project_id)
    if not permanent_storage_dir.exists() and permanent_storage_dir.is_dir():
        raise ValueError(
            f"Project {project_id} directory does not exist in permanent library."
        )

    # If no scan IDs are provided, save all scans in project
    if not scan_ids:
        scan_ids: list[str] = [
            scan_dir.name
            for scan_dir in permanent_storage_dir.glob("*")
            if scan_dir.is_dir()
        ]

    # Check scan exists in permanent library
    for scan_id in scan_ids:
        scan_dir: Path = permanent_storage_dir / str(scan_id)
        if not scan_dir.exists() and scan_dir.is_dir():
            raise ValueError(
                f"Scan {scan_id} directory does not exist in permanent library."
            )

    # Create directories if they do not already exist
    local_prj_dir: Path = local / str(project_id)
    local_scan_dirs: list[Path] = [local_prj_dir / str(scan_id) for scan_id in scan_ids]
    create_dir_if_missing(local_prj_dir)
    for local_scan_dir in local_scan_dirs:
        create_dir_if_missing(local_scan_dir)

    # Find and move data from permanent library to local library
    for scan in scan_ids:
        target: Path = permanent_storage_dir / Path(str(scan))
        destination: Path = local_prj_dir / Path(str(scan))
        logging.info("Moving data from %s to %s", target, destination)
        find_and_move("*", target, destination, copy=True)

    logging.info("Project %s data saved to local library.", project_id)
