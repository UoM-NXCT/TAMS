"""
Runner for dowloading files to the local library.
"""

import logging
import os
import time
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QWidget

from client.utils.hash import hash_in_chunks

from .generic import Worker, WorkerKilledException, WorkerStatus


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
            scan_dir: Path = self.permanent_storage_dir / str(scan_id)
            if not scan_dir.exists() and scan_dir.is_dir():
                raise ValueError(
                    f"Scan {scan_id} directory does not exist in permanent library."
                )

        self.local_prj_dir: Path = local / str(prj_id)
        self.local_scan_dirs: tuple[Path, ...] = tuple(
            self.local_prj_dir / str(scan_id) for scan_id in self.scan_ids
        )

        # Count files to be moved for progress bar
        dlg: QWidget = QWidget()
        msg: QMessageBox = QMessageBox.information(
            dlg,
            "Indexing files",
            "Depending on the size of the data, this may take a long time. Are you sure you would like to continue?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if msg == QMessageBox.StandardButton.Cancel:
            raise ValueError("User cancelled indexing files.")

        logging.info("Indexing files, this may take a while...")
        total_files: int = 0
        size_in_bytes: int = 0
        for scan_id in self.scan_ids:
            scan_dir = self.permanent_storage_dir / str(scan_id)
            # Note: the os.walk method is much faster than Path.rglob
            for root, _, files in os.walk(scan_dir):
                for file in files:
                    total_files += 1
                    file_path = os.path.join(root, file)
                    size_in_bytes += os.stat(file_path).st_size
        self.size_in_bytes: int = size_in_bytes
        try:
            self.set_max_progress(total_files - 1)
        except TypeError as exc:
            # If negative, total_files is 0 and no files are found
            raise ValueError("No files to validate.") from exc

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

                # Skip directories and tams metadata
                if not item.is_dir() and not (
                    item.is_file() and item.parent.name == "tams_metadata"
                ):
                    try:
                        relative_path: Path = item.relative_to(target)
                        local_file: Path = local_dir / "raw" / relative_path

                        # Hash the files
                        target_hash: str = hash_in_chunks(item)
                        local_hash: str = hash_in_chunks(local_file)

                        # Compare hashes
                        if target_hash != local_hash:
                            logging.info(
                                "Hashes do not match: file %s is invalid.", item
                            )
                            self.set_result(False)

                    except FileNotFoundError:
                        logging.info("%s not found, validation fail.", item.name)
                        self.set_result(False)

                # Pause if worker is paused
                while self.worker_status is WorkerStatus.PAUSED:
                    # Keep waiting until resumed
                    time.sleep(0)
                # Check if worker has been killed
                if self.worker_status is WorkerStatus.KILLED:
                    raise WorkerKilledException
                if self.worker_status is WorkerStatus.FINISHED:
                    # Break loop if job is finished
                    return

            if self.worker_status is not WorkerStatus.FINISHED:
                logging.info("Scan %s validated successfully.", scan)

        # If the job reached the end without finishing, it means it was successful
        if self.worker_status is not WorkerStatus.FINISHED:
            logging.info("Validation successful.")
            self.set_result(True)
