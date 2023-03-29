"""Create file download dialogue."""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QStyle

from client.runners import SaveScans
from client.widgets.dialogue import DownloadScans, handle_common_exc

if typing.TYPE_CHECKING:
    from PySide6.QtGui import QIcon

    from client.widgets.main_window import MainWindow


class DownloadData(QAction):
    @handle_common_exc
    def _download(self) -> None:
        """Download action returns a dialogue with a save scans runner.

        This method is called when the action is triggered.
        """
        table: str = self.parent().current_table()

        match table:
            case "scan":
                scan_id: int = self.parent().get_value_from_row(0)
                prj_id: int = self.parent().get_value_from_row(1)
                runner: SaveScans = SaveScans(prj_id, scan_id, download=True)
                DownloadScans(runner, parent_widget=self.parent())
                return
            case "project":
                prj_id = self.parent().get_value_from_row(0)
                runner = SaveScans(prj_id, download=True)
                DownloadScans(runner, parent_widget=self.parent())
                return
            case _:
                # Fallback case for when no valid table is selected
                QMessageBox.critical(
                    self.parent(),
                    "Not implemented error",
                    f"Cannot download data from table {table}",
                )
                raise NotImplementedError("Table must be 'scan' or 'project'.")

    def __init__(self, main_window: MainWindow) -> None:
        """Download data from the server."""
        icon: QIcon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_ArrowDown
        )
        super().__init__(icon, "Download data", main_window)
        self.setShortcut("Ctrl+D")
        self.setToolTip("Download selected data from the server.")
        self.triggered.connect(self._download)
