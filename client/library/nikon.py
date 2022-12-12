from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from client.library.abstract_instrument import AbstractScan


class NikonScan(AbstractScan):
    """Class for Nikon scans."""

    def __init__(self, path: Path) -> None:
        """Initialize the scan.

        :param path: path to the scan
        """
        super().__init__(path)

    def get_metadata(self) -> dict[str, Any]:
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
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()
        voltage_kv: int = int(root.find("XraySettings").find("kV").text)
        current_ua: int = int(root.find("XraySettings").find("uA").text)
        # TODO: parse more metadata from the XML file

        # Parse the XTEKCT file
        # Treat the XTEKCT file as an INI file (I think it is close enough)

        return {
            "voltage": voltage_kv,
            "current": current_ua,
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
            item for item in self.path.glob("*") if self.is_reconstruction(item)
        )

    def get_raw_data(self) -> tuple[Path, ...]:
        """Get the raw data files and directories.

        :return: raw data files and directories
        """

        # Assume that everything that isn't a reconstruction must be raw data
        return tuple(
            item for item in self.path.glob("*") if not self.is_reconstruction(item)
        )


if __name__ == "__main__":
    scan = NikonScan(
        Path(r"Z:\for_archiving\NXCT0462_AG-SDCARD-8gb-Al-1 [2022-11-25 15.49.14]")
    )
    scan.get_metadata()
