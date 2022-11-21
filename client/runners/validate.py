"""
Runner for dowloading files to the local library.

Note: file validation is very slow, so it uses os instead of pathlib.
"""
import glob
import logging
import os
import time
from filecmp import dircmp
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QWidget

from client import settings
from client.utils.hash import hash_in_chunks

from .generic import Worker, WorkerKilledException, WorkerStatus


def has_differences(comparison: dircmp[str]) -> bool:
    """Check if two directories have differences."""

    differences: list[str] = (
        comparison.left_only + comparison.right_only + comparison.diff_files
    )
    if differences:
        return True
    for sub_dir in comparison.subdirs.values():
        if has_differences(sub_dir):
            return True
    return False


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
        self.perm_storage_dir: str = os.path.join(permanent, str(prj_id))
        if not os.path.exists(self.perm_storage_dir) or not os.path.isdir(
            self.perm_storage_dir
        ):
            raise ValueError(
                f"Project {prj_id} directory does not exist in permanent library."
            )

        # If no scan IDs are provided, save all scans in project
        if not scan_ids:
            # Assume each directory in the project directory is a scan
            self.scan_ids: tuple[str, ...] = tuple(
                os.path.basename(scan_dir)
                for scan_dir in glob.glob(os.path.join(self.perm_storage_dir, "*"))
                if os.path.isdir(scan_dir)
            )
        else:
            # Convert list to tuple
            self.scan_ids = tuple(str(scan_id) for scan_id in scan_ids)

        # Check scan exists in permanent library
        for scan_id in self.scan_ids:
            scan_dir: str = os.path.join(self.perm_storage_dir, str(scan_id))
            if not os.path.exists(scan_dir) and os.path.isdir(scan_dir):
                raise ValueError(
                    f"Scan {scan_id} directory does not exist in permanent library."
                )

        self.local_prj_dir: str = os.path.join(local, str(prj_id))
        self.local_scan_dirs: tuple[str, ...] = tuple(
            os.path.join(self.local_prj_dir, scan_id) for scan_id in self.scan_ids
        )

        # Count files to be moved for progress bar
        dlg: QWidget = QWidget()
        msg: QMessageBox.StandardButton = QMessageBox.information(
            dlg,
            "Indexing files",
            "Depending on the size of the data, this may take a long time. Are you sure you would like to continue?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if msg == QMessageBox.StandardButton.Cancel:
            raise ValueError("User cancelled indexing files.")

        total_files: int = 0
        size_in_bytes: int = 0
        for scan_id in self.scan_ids:
            scan_dir = os.path.join(self.perm_storage_dir, str(scan_id))
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
            if not os.path.exists(scan_dir) or not os.path.isdir(scan_dir):
                # If local scan directory does not exist, download is invalid
                logging.info(
                    "Scan directory %s does not exist, validation fail.", scan_dir
                )
                self.set_result(False)
                return

        # Check the contents of each scan directory
        for scan in self.scan_ids:
            target: str = os.path.join(self.perm_storage_dir, scan)
            local_dir: str = os.path.join(
                self.local_prj_dir, str(scan), settings.perm_storage_dir_name
            )

            # Do a shallow identity check (e.g., names and metadata)
            # This doesn't check the contents of the files, but if we catch a difference
            # here, we can be sure that the files are different and skip the lengthy
            # hashing process.
            logging.info("Performing shallow identity check.")
            comparison = dircmp(target, local_dir)
            same = not has_differences(comparison)
            if not same:
                self.set_result(False)
                return

            # Do a deep identity check (e.g., contents of files)
            logging.info("Performing deep identity check.")
            for root, _, files in os.walk(target):
                for file in files:
                    # Increment progress bar
                    self.signals.progress.emit(1)

                    try:
                        relative_path: str = file  # Should be of the form "/..." where "/" is the root of the scan
                        local_file: str = os.path.join(local_dir, relative_path)

                        # Hash the files
                        target_hash: str = hash_in_chunks(
                            os.path.join(root, relative_path)
                        )
                        local_hash: str = hash_in_chunks(local_file)

                        # Compare hashes
                        if target_hash != local_hash:
                            logging.info(
                                "Hashes do not match: file %s is invalid.", file
                            )
                            self.set_result(False)

                    except FileNotFoundError:
                        logging.info(
                            "%s not found, validation fail.", os.path.basename(file)
                        )
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
