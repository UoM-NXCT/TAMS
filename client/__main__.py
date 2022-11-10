"""
Entry point for the GUI application script.
"""

import sys

from PySide6.QtWidgets import QApplication

from client.gui import MainWindow


def main() -> None:
    """Main function implements the GUI."""

    app: QApplication = QApplication(sys.argv)
    main_window: MainWindow = MainWindow()  # pylint: disable=unused-variable
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
