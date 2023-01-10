"""
Toggle full screen mode action.
"""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


class FullScreen(QAction):
    def __init__(self, main_window: MainWindow) -> None:
        """Toggle full screen mode action."""

        super().__init__("&Full Screen", main_window)
        self.setShortcut("F11")
        self.setCheckable(True)
        self.setStatusTip("Toggle full screen mode")
        self.triggered.connect(self.toggle_full_screen)

    def toggle_full_screen(self) -> None:
        """Toggle full screen mode."""

        if self.isChecked():
            self.parent().showFullScreen()
        else:
            self.parent().showNormal()
