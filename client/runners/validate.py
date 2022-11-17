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

from .generic import Worker, WorkerKilledException


class ValidateScansRunner(Worker):
    """Runner that validates data in the local library."""

    def __init__(
        self, local: Path, permanent: Path, prj_id: int, *scan_ids: int
    ) -> None:
        """Initialize the runner."""

        super().__init__(fn=self.job)

        # We can only validate.py scans if the libraries exist!

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

        # If the libraries exist, we still need to check if the project exists

        # Check project exists in permanent library
        self.permanent_storage_dir: Path = permanent / str(prj_id)
        if (
            not self.permanent_storage_dir.exists()
            or not self.permanent_storage_dir.is_dir()
        ):
            raise ValueError(
                f"Project {prj_id} directory does not exist in permanent library."
            )

        # If no scan IDs are provided, save all scans in project
        if not scan_ids:
            # Assume each directory in the project directory is a scan
            self.scan_ids: tuple[str, ...] = tuple(
                scan_dir.name
                for scan_dir in self.permanent_storage_dir.glob("*")
                if scan_dir.is_dir()
            )
        else:
            # Convert list to tuple
            self.scan_ids = tuple(str(scan_id) for scan_id in scan_ids)

        # Check scan exists in permanent library
        for scan_id in self.scan_ids:
            scan_dir: Path = self.permanent_storage_dir / Path(scan_id)
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
            scan_dir: Path = self.permanent_storage_dir / str(scan_id)
            total_files += len(tuple(scan_dir.rglob("*")))
        # Add the scan directories to the total as they are also validated
        total_files += len(self.scan_ids)
        self.set_max_progress(total_files)

    def job(self) -> None:
        """Save data to local library."""

        # Check local scan directories exist
        for scan_dir in self.local_scan_dirs:
            # Increment progress bar
            self.signals.progress.emit(1)
            if not scan_dir.exists():
                # If local scan directory does not exist, download is invalid
                logging.info("Scan directory %s does not exist, validation fail.")
                self.set_result(False)
                return

        # Check the contents of each scan directory
        for scan in self.scan_ids:
            target: Path = self.permanent_storage_dir / Path(scan)
            local_dir: Path = self.local_prj_dir / Path(scan)

            for item in target.rglob("*"):
                # Increment progress bar
                self.signals.progress.emit(1)

                # Skip directories
                if not item.is_dir():
                    # Skip tams metadata
                    if not (item.is_file() and item.parent.name == "tams_metadata"):
                        try:
                            relative_path: Path = item.relative_to(target)
                            local_file: Path = local_dir / relative_path

                            # Hash the files
                            target_hash: str = hash_in_chunks(item)
                            local_hash: str = hash_in_chunks(local_file)

                            # Compare hashes
                            if target_hash != local_hash:
                                logging.info(
                                    "Hashes do not match: file %s is invalid.", item
                                )
                                self.set_result(False)
                            else:
                                logging.info("Hashes match: file %s is valid.", item)

                        except FileNotFoundError:
                            logging.info("%s not found, validation fail.", item.name)
                            self.set_result(False)

                # Pause if worker is paused
                while self.is_paused:
                    # Keep waiting until resumed
                    time.sleep(0)
                # Check if worker has been killed
                if self.is_killed:
                    raise WorkerKilledException
                if self.is_finished:
                    # Break loop if job is finished
                    return

            if not self.is_finished:
                logging.info("Scan %s validated successfully.", scan)

        # If the job reached the end without finishing, it means it was successful
        if not self.is_finished:
            logging.info("Validation successful.")
            self.set_result(True)
