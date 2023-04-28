"""Create file upload dialogue."""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QStyle

from client.runners import SaveScans
from client.widgets.dialogue import UploadScans, handle_common_exc

if typing.TYPE_CHECKING:
    from client.widgets.main_window import MainWindow


class UploadData(QAction):
    """Upload action."""

    @handle_common_exc
    def _upload(self: UploadData) -> None:
        """Download action returns a dialogue with a save scans runner.

        This method is called when the action is triggered.
        """
        table = self.parent().current_table()
        match table:
            case "scan":
                scan_id = self.parent().get_value_from_row(0)
                prj_id = self.parent().get_value_from_row(1)
                runner = SaveScans(prj_id, scan_id, download=False)
                UploadScans(runner, parent_widget=self.parent())
            case "project":
                prj_id = self.parent().get_value_from_row(0)
                runner = SaveScans(prj_id, download=False)
                UploadScans(runner, parent_widget=self.parent())
            case _:
                msg = f"Cannot upload data from table {table}."
                QMessageBox.critical(self.parent(), "Not implemented error", msg)
                raise NotImplementedError(msg)

    def __init__(self: UploadData, main_window: MainWindow) -> None:
        """Upload data to the server."""
        icon = main_window.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        super().__init__(icon, "Upload data", main_window)
        self.setShortcut("Ctrl+U")
        self.setToolTip("Upload selected data to the server.")
        self.triggered.connect(self._upload)
