"""
Entry point for the GUI application script.
"""

import logging
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from client.gui import MainWindow


def main() -> None:
    """Main function implements the GUI."""

    logging.info("Starting application.")
    app: QApplication = QApplication(sys.argv)

    logging.info("Creating main window.")
    main_window: QMainWindow = MainWindow()  # pylint: disable=unused-variable

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
