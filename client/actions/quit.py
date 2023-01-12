from PySide6.QtGui import QAction


class Quit(QAction):
    def __init__(self, main_window) -> None:
        """Quit action."""

        super().__init__("&Quit", main_window)
        self.setShortcut("Ctrl+Q")
        self.triggered.connect(self.parent().close)
