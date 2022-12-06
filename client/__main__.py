"""
Entry point for the GUI application script.
"""
import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from client import settings
from client.gui import MainWindow


def main() -> None:
    """Main function implements the GUI."""

    app: QApplication = QApplication(sys.argv)

    # Create splash screen
    splash = QSplashScreen(QPixmap(settings.splash))
    splash.show()

    app.processEvents()
    _window: MainWindow = MainWindow()
    splash.finish(_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
