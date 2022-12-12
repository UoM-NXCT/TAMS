from pathlib import Path
from typing import Any


class AbstractScan:
    """Base class for all instruments.

    This class defines the interface that all scans must implement.
    """

    def __init__(self, path: Path) -> None:
        """Initialize the instrument.

        :param path: path to the scan
        """
        self.path = path

    def get_reconstructions(self) -> list[list[Path]]:
        """Get the reconstruction files.

        :return: list of reconstruction files
        """
        raise NotImplementedError

    def get_metadata(self) -> dict[str, Any]:
        """Get the metadata for the scan.

        :return: metadata for the scan
        """
        raise NotImplementedError

    def get_raw_data(self) -> list[Path]:
        """Get the raw data files.

        :return: list of raw data files
        """
        raise NotImplementedError

    @staticmethod
    def is_reconstruction(path: Path) -> bool:
        """Check if a path is a reconstruction.

        :param path: path to check
        :return: True if the path is a reconstruction, False otherwise
        """
        raise NotImplementedError
