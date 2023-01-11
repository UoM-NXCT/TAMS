"""
Open documentation in browser action.
"""

from __future__ import annotations

import typing

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QDesktopServices

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


class OpenDocs(QAction):
    @staticmethod
    def _open_docs() -> None:
        """Open documentation in the browser."""

        url: QUrl = QUrl("https://tams-nxct.readthedocs.io/")
        QDesktopServices.openUrl(url)

    def __init__(self, main_window: MainWindow) -> None:
        """Open documentation in browser action."""

        super().__init__("&Open documentation", main_window)
        self.setShortcut("F1")
        self.setStatusTip("Open documentation in browser")
        self.triggered.connect(self._open_docs)
