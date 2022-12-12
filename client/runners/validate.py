"""
Runner for checking that the local and permanent scans are the same.

This involves first doing a shallow check (for example, comparing file names) and then
doing a deep check (comparing file contents) by comparing file hashes.

Note: file validation is very slow, so it uses os instead of pathlib, which is faster.
"""
import errno
import glob
import logging
import os
import time
from filecmp import dircmp
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QWidget

from client import settings
from client.utils.hash import hash_in_chunks

from .generic import GenericRunner, RunnerKilledException, RunnerStatus


class ValidateScans(GenericRunner):
    """Runner that validates data in the local library."""

    def __init__(self, prj_id: int, *scan_ids: int) -> None:
        """Initialize the runner."""

        super().__init__(func=self.job)

        # Store the project ID
        self.prj_id: int = prj_id

        # Store the permanent storage directory name
        self.perm_dir_name: str = settings.get_perm_dir_name()

        self.perm_lib: Path = Path(settings.get_lib("permanent"))
        self.local_lib: Path = Path(settings.get_lib("local"))

        self.perm_prj_dir: str = os.path.join(self.perm_lib, str(self.prj_id))
        self.local_prj_dir: str = os.path.join(self.local_lib, str(self.prj_id))

        # Check library and project directories exist
        self.run_checks()

        # If no scan IDs are provided, save all scans in project
        if not scan_ids:
            # Assume each directory in the project directory is a scan
            perm_scan_ids: tuple[str, ...] = tuple(
                os.path.basename(scan_dir)
                for scan_dir in glob.glob(os.path.join(self.perm_prj_dir, "*"))
                if os.path.isdir(scan_dir)
            )
            local_scan_ids: tuple[str, ...] = tuple(
                os.path.basename(scan_dir)
                for scan_dir in glob.glob(os.path.join(self.local_prj_dir, "*"))
                if os.path.isdir(scan_dir)
            )
            # If validating a project, check each project has the same scans
            if set(perm_scan_ids) == set(local_scan_ids):
                self.scan_ids: tuple[int, ...] = tuple(
                    int(scan_id) for scan_id in perm_scan_ids
                )
            else:
                logging.info(
                    "Permanent scan IDs (%s) do not equal local scan IDs (%s).",
                    perm_scan_ids,
                    local_scan_ids,
                )
                self.set_result(False)
                return
        else:
            # Convert list to tuple
            self.scan_ids = tuple(scan_id for scan_id in scan_ids)

            # Check scan exists in both libraries
            for scan_id in self.scan_ids:
                # Check permanent library
                perm_scan_dir: str = os.path.join(self.perm_prj_dir, str(scan_id))
                if not os.path.exists(perm_scan_dir):
                    raise FileNotFoundError(
                        errno.ENOENT, os.strerror(errno.ENOENT), perm_scan_dir
                    )
                if not os.path.isdir(perm_scan_dir):
                    raise NotADirectoryError(
                        errno.ENOTDIR, os.strerror(errno.ENOTDIR), perm_scan_dir
                    )
                # Check local library
                local_scan_dir: str = os.path.join(self.local_prj_dir, str(scan_id))
                if not os.path.exists(local_scan_dir):
                    raise FileNotFoundError(
                        errno.ENOENT, os.strerror(errno.ENOENT), perm_scan_dir
                    )
                if not os.path.isdir(local_scan_dir):
                    raise NotADirectoryError(
                        errno.ENOTDIR, os.strerror(errno.ENOTDIR), local_scan_dir
                    )

        self.local_scan_dirs: tuple[str, ...] = tuple(
            os.path.join(self.local_prj_dir, str(scan_id)) for scan_id in self.scan_ids
        )

        # Count files to be moved for progress bar
        dlg: QWidget = QWidget()
        response: QMessageBox.StandardButton = QMessageBox.information(
            dlg,
            "Indexing files",
            (
                "Depending on the size of the data, this may take a long time. Are you"
                " sure you would like to continue?"
            ),
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if response == QMessageBox.StandardButton.Cancel:
            raise InterruptedError("User cancelled validation.")
        dlg.close()

        total_files: int = 0
        self.size_in_bytes: int = 0
        for scan_id in self.scan_ids:
            perm_scan_dir = os.path.join(self.perm_prj_dir, str(scan_id))
            # Note: the os.walk method is much faster than Path.rglob
            for root, _, files in os.walk(perm_scan_dir):
                total_files += len(files)
                for file in files:
                    file_path = os.path.join(root, file)
                    self.size_in_bytes += os.stat(file_path).st_size
        if not total_files or not self.size_in_bytes:
            # If negative, total_files is 0 and no files are found
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.local_prj_dir
            )
        self.set_max_progress(total_files - 1)

    def run_checks(self) -> None:
        """Check if directories exist before validating files."""

        # Check if libraries exist
        if not self.local_lib.exists():
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.local_lib
            )
        if not self.perm_lib.exists():
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.perm_lib
            )

        # Check if libraries are directories
        if not self.local_lib.is_dir():
            raise NotADirectoryError(
                errno.ENOTDIR, os.strerror(errno.ENOTDIR), self.local_lib
            )
        if not self.perm_lib.is_dir():
            raise NotADirectoryError(
                errno.ENOTDIR, os.strerror(errno.ENOTDIR), self.perm_lib
            )

        # Check project exists in permanent library
        if not os.path.exists(self.perm_lib):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.perm_lib
            )
        if not os.path.isdir(self.perm_lib):
            raise NotADirectoryError(
                errno.ENOTDIR, os.strerror(errno.ENOTDIR), self.perm_lib
            )

    @classmethod
    def has_differences(cls, comparison: dircmp[str]) -> bool:
        """Check if two directories have differences."""

        differences: list[str] = (
            comparison.left_only + comparison.right_only + comparison.diff_files
        )
        if differences:
            return True
        for sub_dir in comparison.subdirs.values():
            # Recursively check subdirectories
            if cls.has_differences(sub_dir):
                return True
        return False

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

        # Check scan meta
        for scan_id in self.scan_ids:
            perm_dir: str = os.path.join(self.perm_prj_dir, str(scan_id), "tams_meta")
            local_dir: str = os.path.join(self.local_prj_dir, str(scan_id), "tams_meta")
            for root, _, files in os.walk(perm_dir):
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
                    while self.worker_status is RunnerStatus.PAUSED:
                        # Keep waiting until resumed
                        time.sleep(0)
                    # Check if worker has been killed
                    if self.worker_status is RunnerStatus.KILLED:
                        raise RunnerKilledException
                    if self.worker_status is RunnerStatus.FINISHED:
                        # Break loop if job is finished
                        return

        # Check the contents of each scan directory
        for scan_id in self.scan_ids:
            perm_dir = os.path.join(
                self.perm_prj_dir, str(scan_id), settings.get_perm_dir_name()
            )
            # Local directory appended with subdirectory
            local_dir = os.path.join(
                self.local_prj_dir, str(scan_id), settings.get_perm_dir_name()
            )

            # Do a shallow identity check (e.g., names and metadata)
            # This doesn't check the contents of the files, but if we catch a difference
            # here, we can be sure that the files are different and skip the lengthy
            # hashing process.
            logging.info("Performing shallow identity check.")
            comparison = dircmp(perm_dir, local_dir)
            same = not self.has_differences(comparison)
            if not same:
                logging.info("Shallow identity check failed.")
                self.set_result(False)
                return

            # Do a deep identity check (e.g., contents of files)
            logging.info("Performing deep identity check.")
            for root, _, files in os.walk(perm_dir):
                for file in files:
                    # Increment progress bar
                    self.signals.progress.emit(1)

                    try:
                        relative_path = file  # Should be of the form "/..." where "/" is the root of the scan
                        local_file = os.path.join(local_dir, relative_path)

                        # Hash the files
                        target_hash = hash_in_chunks(os.path.join(root, relative_path))
                        local_hash = hash_in_chunks(local_file)

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
                    while self.worker_status is RunnerStatus.PAUSED:
                        # Keep waiting until resumed
                        time.sleep(0)
                    # Check if worker has been killed
                    if self.worker_status is RunnerStatus.KILLED:
                        raise RunnerKilledException
                    if self.worker_status is RunnerStatus.FINISHED:
                        # Break loop if job is finished
                        return

            if self.worker_status is not RunnerStatus.FINISHED:
                logging.info("Scan %s validated successfully.", scan_id)

        # If the job reached the end without finishing, it means it was successful
        if self.worker_status is not RunnerStatus.FINISHED:
            logging.info("Validation successful.")
            self.set_result(True)
