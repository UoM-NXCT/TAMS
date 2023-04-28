"""Quit action."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QAction

if TYPE_CHECKING:
    from client.widgets.main_window import MainWindow


class Quit(QAction):
    """Quit action."""

    def __init__(self: Quit, main_window: MainWindow) -> None:
        """Initialize the action."""
        super().__init__("&Quit", main_window)
        self.setShortcut("Ctrl+Q")
        self.triggered.connect(self.parent().close)
