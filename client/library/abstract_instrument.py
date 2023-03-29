"""Abstract scan class."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


class AbstractScan:
    """Base class for all scans.

    This class defines the interface that all scans must implement.
    """

    def __init__(self, path: Path) -> None:
        """Initialize the instrument.

        :param path: path to the scan
        """
        self.path = path

    def get_reconstructions(self) -> tuple[Path, ...]:
        """Get the reconstruction files.

        :return: list of reconstruction files
        """
        raise NotImplementedError

    def get_metadata(self) -> dict[str, Any] | None:
        """Get the metadata for the scan.

        :return: metadata for the scan
        """
        raise NotImplementedError

    def get_raw_data(self) -> tuple[Path, ...]:
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
