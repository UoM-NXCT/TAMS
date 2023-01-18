"""
About dialogue for the application.
"""
from datetime import date

from PySide6.QtWidgets import QDialog, QMessageBox

from client import __version__


class About(QDialog):
    """About dialogue."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the dialogue."""

        super().__init__(*args, **kwargs)

        title: str = "About this software"
        msg: str = self.get_msg()

        QMessageBox.about(self, title, msg)

    @staticmethod
    def get_msg() -> str:
        """Get the message to display in the dialogue."""

        # Copyright information
        current_year: int = date.today().year
        if current_year > 2022:
            year: str = f"2022 &ndash; {current_year}"
        else:
            year = "2022"

        # Licence information
        licence_href: str = "https://github.com/UoM-NXCT/TAMS/blob/main/LICENCE"
        licence_link: str = f"<a href='{licence_href}'>MIT licence</a>"

        # Warranty information
        warranty: str = (
            "This software is distributed without any warranty, express or implied. In"
            " no event shall the authors or copyright holders be liable for any"
            " claim,damages, or other liability arising from, out of, or in connection"
            " with the software or the use or other dealings in the software."
        )

        return f"""
            <h3>Tomography Archival and Management Software (TAMS)</h3>
            <h4>Version {__version__}</h4>
            <p>Original author: Tom Kuson.</p>
            <p>
                &copy; {year} National X-ray Computed Tomography et al.
                <br>
                This software is open-source and released under the {licence_link}.
            </p>
            <p>{warranty}</p>
        """
