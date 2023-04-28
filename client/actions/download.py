"""Create file download dialogue."""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QStyle

from client.runners import SaveScans
from client.widgets.dialogue import DownloadScans, handle_common_exc

if typing.TYPE_CHECKING:
    from client.widgets.main_window import MainWindow


class DownloadData(QAction):
    """Download action."""

    @handle_common_exc
    def _download(self: DownloadData) -> None:
        """Download action returns a dialogue with a save scans runner.

        This method is called when the action is triggered.
        """
        table = self.parent().current_table()

        match table:
            case "scan":
                scan_id: int = self.parent().get_value_from_row(0)
                prj_id: int = self.parent().get_value_from_row(1)
                runner: SaveScans = SaveScans(prj_id, scan_id, download=True)
                DownloadScans(runner, parent_widget=self.parent())
            case "project":
                prj_id = self.parent().get_value_from_row(0)
                runner = SaveScans(prj_id, download=True)
                DownloadScans(runner, parent_widget=self.parent())
            case _:
                msg = f"Cannot download data from table {table}."
                QMessageBox.critical(self.parent(), "Not implemented error", msg)
                raise NotImplementedError(msg)

    def __init__(self: DownloadData, main_window: MainWindow) -> None:
        """Download data from the server."""
        icon = main_window.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        super().__init__(icon, "Download data", main_window)
        self.setShortcut("Ctrl+D")
        self.setToolTip("Download selected data from the server.")
        self.triggered.connect(self._download)
