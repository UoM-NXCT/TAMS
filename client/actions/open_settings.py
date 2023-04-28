"""Open settings action."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QAction

from client.widgets.dialogue import Settings

if TYPE_CHECKING:
    from client.widgets.main_window import MainWindow


class OpenSettings(QAction):
    """Open settings action."""

    def __init__(self: OpenSettings, main_window: MainWindow) -> None:
        """Open settings action."""
        super().__init__("&Settings", main_window)
        self.setShortcut("Ctrl+Shift+S")
        self.triggered.connect(lambda: Settings(parent=main_window))
