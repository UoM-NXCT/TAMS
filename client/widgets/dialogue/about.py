"""
About dialogue for the application.
"""
from datetime import date

from PySide6.QtWidgets import QDialog, QMessageBox

from client import __version__


class About(QDialog):
    """About dialogue."""

    def __init__(self) -> None:
        """Initialize the about dialogue."""

        super().__init__(parent=None)

        title: str = "About this software"

        current_year: int = date.today().year

        msg: str = f"""
            <h3>Tomography Archival and Management Software (TAMS)</h3>
            <h4>Version {__version__}</h4>
            <p>Original author: Tom Kuson (The University of Manchester).</p>
            <p>
            Copyright &copy; {current_year} National X-ray Computed Tomography et al.
            <br>
            This software is open-source and released under the 
                <a href='https://github.com/UoM-NXCT/TAMS/blob/main/LICENCE'>
                MIT licence
                </a>.
            </p>
            <p>
            This software is distributed without any warranty, express or implied. In 
            no event shall the authors or copyright holders be liable for any claim, 
            damages, or other liability arising from, out of, or in connection with the 
            software or the use or other dealings in the software.
            </p>
        """

        # Create a message box
        QMessageBox.about(self, title, msg)
