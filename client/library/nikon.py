from __future__ import annotations

from configparser import ConfigParser
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree

from .abstract_instrument import AbstractScan

if TYPE_CHECKING:
    from pathlib import Path
    from xml.etree.ElementTree import Element


class NikonScan(AbstractScan):
    """Class for Nikon scans."""

    def __init__(self, path: Path) -> None:
        """Initialize the scan.

        :param path: path to the scan
        """
        self.path = path
        super().__init__(path)

    def get_metadata(self) -> dict[str, Any] | None:
        """Get the metadata for the scan.

        :return: metadata for the scan
        """

        # The metadata we want to extract is in two files

        # First, we need to find the ctprofile XML file
        try:
            xml_file = next(self.path.glob("*.ctprofile.xml"))
        except StopIteration as exc:
            raise FileNotFoundError("Could not find .ctprofile.xml file") from exc

        # Second, we need to find the XTEKCT file
        try:
            xtekct_file = next(self.path.glob("*.xtekct"))
        except StopIteration as exc:
            raise FileNotFoundError("Could not find .xtekct file") from exc

        # Parse the XML file
        # This not secure against maliciously constructed data; assume XML data is safe
        tree = ElementTree.parse(xml_file)
        root: Element = tree.getroot()
        try:
            settings = root.find("XraySettings")
            voltage_kv: int = int(settings.find("kV").text)  # type: ignore
            current_ua: int = int(settings.find("uA").text)  # type: ignore
        except (AttributeError, TypeError):
            # If we can't find the voltage and current, we can't get the metadata
            return None
        # TODO: parse more metadata from the XML file

        # Parse the XTEKCT file
        # Treat the XTEKCT file as an INI file (I think it is close enough)
        xtekct_data: ConfigParser = ConfigParser()
        xtekct_data.read(xtekct_file)
        scan_name: str = xtekct_data["XTekCT"]["Name"]
        # TODO: parse more metadata from the XTEKCT file

        return {
            "voltage": voltage_kv,
            "amperage": current_ua,
            "scan_name": scan_name,
        }

    @staticmethod
    def is_reconstruction(path: Path) -> bool:
        """
        For Nikon, assume all directories with an underscore are reconstructions
        For example, "reconxx_01" is a reconstruction; "reconxx" is not
        """
        return path.is_dir() and "_" in path.name

    def get_reconstructions(self) -> tuple[Path, ...]:
        """Get the reconstruction directories.

        :return: list of reconstruction directories
        """

        return tuple(
            item.relative_to(self.path)
            for item in self.path.glob("*")
            if self.is_reconstruction(item)
        )

    def get_raw_data(self) -> tuple[Path, ...]:
        """Get the raw data files and directories.

        :return: raw data files and directories
        """

        # Assume that everything that isn't a reconstruction must be raw data
        return tuple(
            item for item in self.path.glob("*") if not self.is_reconstruction(item)
        )
