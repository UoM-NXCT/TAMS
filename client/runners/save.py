"""
Runner for dowloading files to the local library.
"""

import time
from pathlib import Path
from typing import Any

from client import settings
from client.db.utils import dict_to_conn_str
from client.db.views import DatabaseView
from client.runners.generic import Worker, WorkerKilledException, WorkerStatus
from client.utils.file import create_dir_if_missing, move_item
from client.utils.toml import create_toml, get_dict_from_toml


class DownloadScansWorker(Worker):
    """Runner that downloads data to the local library."""

    def __init__(
        self, local: Path, permanent: Path, prj_id: int, *scan_ids: int
    ) -> None:
        """Initialize the runner."""

        super().__init__(fn=self.job)

        # We can only download scans if the libraries exist!

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
            scan_dir: Path = self.permanent_storage_dir / str(scan_id)
            if not scan_dir.exists() and scan_dir.is_dir():
                raise ValueError(
                    f"Scan {scan_id} directory does not exist in permanent library."
                )

        # Create directories if they do not already exist
        self.local_prj_dir: Path = local / str(prj_id)
        local_scan_dirs: tuple[Path, ...] = tuple(
            self.local_prj_dir / str(scan_id) for scan_id in self.scan_ids
        )
        create_dir_if_missing(self.local_prj_dir)
        for local_scan_dir in local_scan_dirs:
            create_dir_if_missing(local_scan_dir)

        # Count files to be moved for progress bar
        total_files: int = 0
        for scan_id in self.scan_ids:
            total_files += len(tuple(self.permanent_storage_dir.glob(f"{scan_id}/*")))
        self.set_max_progress(total_files)

    def get_scan_form_data(self, scan_id: int) -> dict[str, dict[str, Any]]:
        """Get the metadata for a scan."""
        conn_dict: dict[str, dict[str, Any]] = get_dict_from_toml(settings.database)
        conn_str: str = dict_to_conn_str(conn_dict)
        db = DatabaseView(conn_str)
        return db.get_scan_form_data(scan_id)

    def job(self) -> None:
        """Save data to local library."""

        # Save each scan in scan list
        for scan in self.scan_ids:

            # Target the scan directory in the permanent library
            target: Path = self.permanent_storage_dir / Path(scan)

            # Save to local library
            destination: Path = self.local_prj_dir / Path(scan)

            # Create user form
            create_dir_if_missing(destination / "tams_meta")
            user_form: Path = destination / "tams_meta" / "user_form.toml"
            scan_form_data: dict[str, Any] = self.get_scan_form_data(int(scan))
            create_toml(user_form, scan_form_data)

            # Move files
            for item in target.glob("*"):

                # Move item
                move_item(item, destination, keep_original=True)

                # Increment progress bar
                self.signals.progress.emit(1)

                # Pause if worker is paused
                while self.worker_status is WorkerStatus.PAUSED:
                    # Keep waiting until resumed
                    time.sleep(0)

                # Check if worker has been killed
                if self.worker_status is WorkerStatus.KILLED:
                    raise WorkerKilledException
                if self.worker_status is WorkerStatus.FINISHED:
                    # Break loop if job is finished
                    break
