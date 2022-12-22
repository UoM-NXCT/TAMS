"""
Runner for adding scans to the local library and the database.
"""

from client.library import AbstractScan, get_relative_path, local_path
from client.utils.file import move_item

from .generic import GenericRunner


class AddScan(GenericRunner):
    def __init__(self, prj_id: int, scan_id: int, scan: AbstractScan):
        """Initialize the runner."""

        super().__init__(func=self.job)

        # Store the project ID
        self.prj_id: int = prj_id

        # Store the scan ID
        self.scan_id: int = scan_id

        # Store the scan
        self.scan: AbstractScan = scan

    def job(self) -> None:
        directory = local_path(get_relative_path(self.prj_id, self.scan_id))
        # TODO: For now we download everything, but this should be up to the user.
        reconstruction_data = self.scan.get_reconstructions()
        print(reconstruction_data)
        for item in reconstruction_data:
            new_location = directory / "reconstructions"
            move_item(self.scan.path / item, new_location, keep_original=True)
        print("Done")
