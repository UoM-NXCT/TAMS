"""
Runner for dowloading files to the local library.
"""

import time
from pathlib import Path

from client.utils.file import create_dir_if_missing, move_or_copy_item

from .abstract import AbstractJobRunner, WorkerKilledException


class DownloadScansRunner(AbstractJobRunner):
    """Runner that downloads data to the local library."""

    def __init__(self, local: Path, permanent: Path, project_id: int, *scan_ids):
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
        self.permanent_storage_dir: Path = permanent / str(project_id)
        if (
            not self.permanent_storage_dir.exists()
            and self.permanent_storage_dir.is_dir()
        ):
            raise ValueError(
                f"Project {project_id} directory does not exist in permanent library."
            )

        # If no scan IDs are provided, save all scans in project
        if not scan_ids:
            self.scan_ids: list[str] = [
                scan_dir.name
                for scan_dir in self.permanent_storage_dir.glob("*")
                if scan_dir.is_dir()
            ]
        else:
            self.scan_ids = scan_ids

        # Check scan exists in permanent library
        for scan_id in self.scan_ids:
            scan_dir: Path = self.permanent_storage_dir / str(scan_id)
            if not scan_dir.exists() and scan_dir.is_dir():
                raise ValueError(
                    f"Scan {scan_id} directory does not exist in permanent library."
                )

        # Create directories if they do not already exist
        self.local_prj_dir: Path = local / str(project_id)
        local_scan_dirs: list[Path] = [
            self.local_prj_dir / str(scan_id) for scan_id in self.scan_ids
        ]
        create_dir_if_missing(self.local_prj_dir)
        for local_scan_dir in local_scan_dirs:
            create_dir_if_missing(local_scan_dir)

        # Count files to be moved
        total_files: int = 0
        for scan_id in self.scan_ids:
            total_files += len(list(self.permanent_storage_dir.glob(f"{scan_id}/*")))
        self.max_progress = total_files

    def job(self):
        """Save data to local library."""

        for scan in self.scan_ids:
            target: Path = self.permanent_storage_dir / Path(str(scan))
            destination: Path = self.local_prj_dir / Path(str(scan))
            for item in target.glob("*"):
                time.sleep(0)
                move_or_copy_item(item, destination, keep_original=True)
                # Increment progress bar
                self.signals.progress.emit(1)
                while self.is_paused:
                    time.sleep(0.1)
                if self.is_killed:
                    raise WorkerKilledException
                if self.is_finished:
                    # Break loop if job is finished
                    break
        self.finish()
