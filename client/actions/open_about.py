from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QStyle

from client.widgets.dialogue import About

if TYPE_CHECKING:
    from client.widgets.main_window import MainWindow


class OpenAbout(QAction):
    def __init__(self, main_window: MainWindow) -> None:
        """Open about action."""

        icon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_MessageBoxInformation
        )
        super().__init__(icon, "&About", main_window)
        self.setShortcut("Ctrl+Shift+A")
        self.setStatusTip("Open about dialogue")
        self.triggered.connect(lambda: About(parent=main_window))
