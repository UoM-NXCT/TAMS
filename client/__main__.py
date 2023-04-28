"""Entry point for the GUI application script."""

import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from client import settings
from client.widgets.main_window import MainWindow


def main() -> None:
    """Implement the GUI."""
    app = QApplication(sys.argv)
    splash = QSplashScreen(QPixmap(settings.splash))
    splash.show()
    app.processEvents()
    window = MainWindow()
    splash.finish(window)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
