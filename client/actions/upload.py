"""
Create file upload dialogue.
"""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QStyle

from client.runners import SaveScans
from client.widgets.dialogue import UploadScans, handle_common_exc

if typing.TYPE_CHECKING:
    from client.widgets.main_window import MainWindow


class UploadData(QAction):
    @handle_common_exc
    def _upload(self) -> None:
        """Download action returns a dialogue with a save scans runner.

        This method is called when the action is triggered.
        """

        table: str = self.parent().current_table()

        match table:
            case "scan":
                scan_id: int = self.parent().get_value_from_row(0)
                prj_id: int = self.parent().get_value_from_row(1)
                runner: SaveScans = SaveScans(prj_id, scan_id, download=False)
                UploadScans(runner, parent_widget=self.parent())
                return
            case "project":
                prj_id = self.parent().get_value_from_row(0)
                runner = SaveScans(prj_id, download=False)
                UploadScans(runner, parent_widget=self.parent())
                return
            case _:
                # Fallback case for when no valid table is selected
                QMessageBox.critical(
                    self.parent(),
                    "Not implemented error",
                    f"Cannot upload data from table {table}",
                )
                raise NotImplementedError("Table must be 'scan' or 'project'.")

    def __init__(self, main_window: MainWindow) -> None:
        """Upload data to the server."""

        icon = main_window.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        super().__init__(icon, "Upload data", main_window)
        self.setShortcut("Ctrl+U")
        self.setToolTip("Upload selected data to the server.")
        self.triggered.connect(self._upload)
