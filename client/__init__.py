"""
Evaluate run-time constants.
"""
import sys
from importlib import metadata
from typing import TYPE_CHECKING

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from client import settings
from client.gui import MainWindow
from client.utils import log

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow


# Get the version of the package
try:
    # FIXME: This doesn't seem to work and raises an exception (see below).
    __version__: str = metadata.version(__name__)
except metadata.PackageNotFoundError:
    log.logger(__name__).error(
        "Could not find %s metadata during init. Setting version to 'unknown'.",
        __name__,
    )
    __version__ = "unknown"


def main() -> None:
    """Main function implements the GUI."""

    app: QApplication = QApplication(sys.argv)
    splash: QSplashScreen = QSplashScreen(QPixmap(settings.splash))
    splash.show()
    app.processEvents()
    window: QMainWindow = MainWindow()
    splash.finish(window)

    sys.exit(app.exec())
