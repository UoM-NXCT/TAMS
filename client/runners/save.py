"""
Runner for uploading and downloading files to the permanent or local library.
"""
import errno
import logging
import os
import time
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import QMessageBox, QWidget

from client import settings
from client.db.utils import dict_to_conn_str
from client.db.views import DatabaseView
from client.utils.file import create_dir, move_item
from client.utils.toml import load_toml

from .generic import GenericRunner, RunnerKilledException, RunnerStatus


class SaveScans(GenericRunner):
    """Runner that downloads data to the local library."""

    def __init__(
        self,
        prj_id: int,
        *scan_ids: int,
        download: bool,
    ) -> None:
        """Initialize the runner."""

        super().__init__(func=self.job)

        # Store the project ID
        self.prj_id: int = prj_id

        # Store download flag
        self.download: bool = download

        # Store the permanent storage directory name
        self.perm_dir_name: str = settings.get_perm_dir_name()

        if not self.download:
            # If uploading, the source is the raw scans dir in the root scan dir
            self.glob_arg: str = f"{self.perm_dir_name}/*"
        else:
            self.glob_arg = "*"

        perm_lib: Path = Path(settings.get_lib("permanent"))
        local_lib: Path = Path(settings.get_lib("local"))

        if self.download:
            # If downloading, the source is the permanent library
            self.source_lib: Path = perm_lib
            self.dest_lib: Path = local_lib
        else:
            # If uploading, the source is the local library
            self.source_lib = local_lib
            self.dest_lib = perm_lib

        # Store the source and destination project directories
        self.source_prj_dir: Path = self.source_lib / str(prj_id)
        self.dest_prj_dir: Path = self.dest_lib / str(prj_id)

        # Store the scan IDs of the scans to be saved
        if scan_ids:
            # Convert list to tuple
            self.scan_ids: tuple[str, ...] = tuple(str(scan_id) for scan_id in scan_ids)
        else:
            # If no scans are specified, save all scans
            # Assume each directory in the project directory is a scan
            self.scan_ids = tuple(
                scan_dir.name
                for scan_dir in self.source_prj_dir.glob("*")
                if scan_dir.is_dir()
            )

        # Check required directories exist
        self.run_checks()

        # Create directories in destination library if they do not already exist
        create_dir(self.dest_prj_dir)
        for scan_id in self.scan_ids:
            create_dir(self.dest_prj_dir / str(scan_id))

        # Count files to be moved for progress bar
        # This can take a long time, so ask user if they want to continue
        dlg: QWidget = QWidget()
        response: QMessageBox.StandardButton = QMessageBox.information(
            dlg,
            "Indexing files",
            (
                "Depending on the size of the data, this may take a long time."
                "Are you sure you would like to continue?"
            ),
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if response == QMessageBox.StandardButton.Cancel:
            raise ValueError("User cancelled indexing files.")
        dlg.close()

        logging.info(
            "Indexing files in %s, this may take a while...", self.source_prj_dir
        )
        total_files: int = 0
        self.size_in_bytes: int = 0
        for scan_id in self.scan_ids:
            scan_dir = self.source_prj_dir / str(scan_id) / self.perm_dir_name
            # Note: the os.walk method is much faster than Path.rglob
            for root, _, files in os.walk(scan_dir):
                # Add number of files in the directory to total
                total_files += len(files)
                # Add size of files in the directory to total
                for file in files:
                    file_path = os.path.join(root, file)
                    self.size_in_bytes += os.stat(file_path).st_size
        if not total_files or not self.size_in_bytes:
            logging.warning("No files found in %s", self.source_prj_dir)
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.source_prj_dir
            )
        self.set_max_progress(total_files - 1)  # Count from 0

    def run_checks(self) -> None:
        """Check if the directories exist before saving files."""

        # Saving from one library to another is only possible if the libraries exist
        local_lib: Path = Path(settings.get_lib("local"))
        perm_lib: Path = Path(settings.get_lib("permanent"))

        # Check if libraries exist
        if not local_lib.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), local_lib)
        if not perm_lib.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), perm_lib)

        # Check if libraries are directories
        if not local_lib.is_dir():
            raise NotADirectoryError(
                errno.ENOTDIR, os.strerror(errno.ENOTDIR), local_lib
            )
        if not perm_lib.is_dir():
            raise NotADirectoryError(
                errno.ENOTDIR, os.strerror(errno.ENOTDIR), perm_lib
            )

        # If the libraries exist, we still need to check if the project exists
        # Check project exists in source library
        if not self.source_prj_dir.exists():
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.source_prj_dir
            )
        if not self.source_prj_dir.is_dir():
            raise NotADirectoryError(
                errno.ENOTDIR, os.strerror(errno.ENOTDIR), self.source_prj_dir
            )

        # Check scan directories exist in source library
        for scan_id in self.scan_ids:
            scan_dir: Path = self.source_lib / str(scan_id)
            if not scan_dir.exists() and scan_dir.is_dir():
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), scan_dir
                )

        # Don't check if dirs exist in the destination lib; they will be created if not

    @staticmethod
    def get_scan_form_data(scan_id: int) -> dict[str, dict[str, Any]]:
        """Get the metadata for a scan."""

        conn_dict: dict[str, dict[str, Any]] = load_toml(settings.database)
        conn_str: str = dict_to_conn_str(conn_dict)
        db = DatabaseView(conn_str)
        return db.get_scan_form_data(scan_id)

    def job(self) -> None:
        """Save data from source to destination library."""

        # Save each scan in scan list
        for scan in self.scan_ids:
            # Target the scan directory in the source library
            source_scan_dir: Path = self.source_prj_dir / Path(scan)

            # Save to local library
            dest_scan_dir: Path = self.dest_prj_dir / Path(scan)

            # Copy metadata
            for item in (source_scan_dir / "tams_meta").glob("*"):
                dest_path: Path = dest_scan_dir / "tams_meta"
                move_item(item, dest_path, keep_original=True)

            # Move files
            for item in source_scan_dir.rglob(self.glob_arg):
                # Move item
                if not item.is_file():
                    # Skip directories
                    continue
                dest = dest_scan_dir / self.perm_dir_name

                move_item(item, dest, keep_original=True)

                # Increment progress bar
                self.signals.progress.emit(1)

                # Pause if worker is paused
                while self.worker_status is RunnerStatus.PAUSED:
                    # Keep waiting until resumed
                    time.sleep(0)

                # Check if worker has been killed
                if self.worker_status is RunnerStatus.KILLED:
                    raise RunnerKilledException
                if self.worker_status is RunnerStatus.FINISHED:
                    # Break loop if job is finished
                    break
            else:
                print("shit")
