"""
Runner for dowloading files to the local library.
"""

import logging
import time
from pathlib import Path
from typing import Any

from client import settings
from client.db.utils import dict_to_conn_str
from client.db.views import DatabaseView
from client.utils.file import create_dir_if_missing, move_item
from client.utils.hash import hash_in_chunks
from client.utils.toml import create_toml, get_dict_from_toml

from .abstract import AbstractJobRunner, WorkerKilledException


class ValidateScansRunner(AbstractJobRunner):
    """Runner that validates data in the local library."""

    def __init__(
        self, local: Path, permanent: Path, prj_id: int, *scan_ids: int
    ) -> None:
        """Initialize the runner."""

        super().__init__()

        # Check if libraries exist
        if not local.exists():
            raise ValueError(f"Local library directory {local} does not exist.")
        if not permanent.exists():
            raise ValueError(f"Permanent library directory {permanent} does not exist.")

        # Check if library directories are actually directories
        if not local.is_dir():
            raise ValueError(f"Local library directory {local} is not a directory.")
        if not permanent.is_dir():
            raise ValueError(
                f"Permanent library directory {permanent} is not a directory."
            )

        # Check project exists in permanent library
        self.permanent_storage_dir: Path = permanent / str(prj_id)
        if (
            not self.permanent_storage_dir.exists()
            and self.permanent_storage_dir.is_dir()
        ):
            raise ValueError(
                f"Project {prj_id} directory does not exist in permanent library."
            )

        # If no scan IDs are provided, check all scans in project
        if not scan_ids:
            self.scan_ids: tuple[str, ...] = tuple(
                scan_dir.name
                for scan_dir in self.permanent_storage_dir.glob("*")
                if scan_dir.is_dir()
            )
        else:
            self.scan_ids = tuple(str(scan_id) for scan_id in scan_ids)

        # Check scan exists in permanent library
        for scan_id in self.scan_ids:
            scan_dir: Path = self.permanent_storage_dir / str(scan_id)
            if not scan_dir.exists() and scan_dir.is_dir():
                raise ValueError(
                    f"Scan {scan_id} directory does not exist in permanent library."
                )

        self.local_prj_dir: Path = local / str(prj_id)
        self.local_scan_dirs: tuple[Path, ...] = tuple(
            self.local_prj_dir / str(scan_id) for scan_id in self.scan_ids
        )

        # Count files to be validated
        total_files: int = 0
        for scan_id in self.scan_ids:
            total_files += len(tuple(self.permanent_storage_dir.glob(f"{scan_id}/*")))
        self.max_progress = total_files

    def job(self) -> None:
        """Save data to local library."""

        # Check local scan directories exist
        for scan_dir in self.local_scan_dirs:
            if not scan_dir.exists():
                self.result(False)
                self.signals.finished.emit()

        for scan in self.scan_ids:
            target: Path = self.permanent_storage_dir / Path(scan)
            destination: Path = self.local_prj_dir / Path(scan)

            for item in target.rglob("*"):
                # Increment progress bar
                self.signals.progress.emit(1)

                # Skip tams metadata
                if item.is_file() and item.parent.name == "tams_metadata":
                    continue
                if item.is_dir() and item.name == "tams_metadata":
                    continue

                try:
                    relative_path: Path = item.relative_to(target)
                    item_destination: Path = destination / relative_path

                    # Hash the files
                    target_hash: str = hash_in_chunks(item)
                    destination_hash: str = hash_in_chunks(item_destination)

                    # Compare hashes
                    if target_hash != destination_hash:
                        logging.info("Hashes do not match.")
                        self.result(False)
                        self.signals.finished.emit()

                except FileNotFoundError:
                    logging.info("File not found, validation fail.")
                    self.result(False)
                    self.signals.finished.emit()



                while self.is_paused:
                    time.sleep(0)
                if self.is_killed:
                    raise WorkerKilledException
                if self.is_finished:
                    # Break loop if job is finished
                    break
        self.finish()
