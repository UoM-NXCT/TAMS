"""Runner for adding scans to the local library and the database."""
from __future__ import annotations

from typing import TYPE_CHECKING

from client.library import get_relative_path, local_path
from client.utils.file import move_item

from .generic import GenericRunner

if TYPE_CHECKING:
    from client.library import AbstractScan


class AddScan(GenericRunner):
    def __init__(self, prj_id: int, scan_id: int, scan: AbstractScan) -> None:
        """Initialize the runner."""
        super().__init__(func=self.job)

        # Store the project ID
        self.prj_id: int = prj_id

        # Store the scan ID
        self.scan_id: int = scan_id

        # Store the scan
        self.scan: AbstractScan = scan

    def job(self) -> None:
        """Add the scan to the local library."""
        directory = local_path(get_relative_path(self.prj_id, self.scan_id))
        # TODO: For now we download everything, but this should be up to the user.
        recon_data = self.scan.get_reconstructions()
        for item in recon_data:
            new_location = directory / "reconstructions"
            move_item(self.scan.path / item, new_location, keep_original=True)
        raw_data = self.scan.get_raw_data()
        for item in raw_data:
            new_location = directory / "raw"
            move_item(self.scan.path / item, new_location, keep_original=True)
