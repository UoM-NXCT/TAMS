from PySide6.QtGui import QAction


class Quit(QAction):
    def __init__(self, main_window):
        """Quit action."""

        super().__init__("&Quit", main_window)
        self.setShortcut("Ctrl+Q")
        self.triggered.connect(main_window.close)  # close is a method of QMainWindow
