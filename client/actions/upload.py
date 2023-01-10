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
    from client.gui import MainWindow


@handle_common_exc
def upload(main_window: MainWindow) -> UploadScans:
    """Download action returns a dialogue with a save scans runner."""

    # Get the selected table
    table: str = main_window.current_table()

    match table:
        case "scan":
            # Get the selected scan
            scan_id: int = main_window.get_value_from_row(0)
            prj_id: int = main_window.get_value_from_row(1)

            # Return the scan download dialogue
            runner: SaveScans = SaveScans(prj_id, scan_id, download=False)
            return UploadScans(runner, parent_widget=main_window)

        case "project":
            # Get the selected project
            prj_id = main_window.get_value_from_row(0)

            # Return the project download dialogue
            runner = SaveScans(prj_id, download=False)
            return UploadScans(runner, parent_widget=main_window)

        case _:
            # Fallback case for when no valid table is selected
            QMessageBox.critical(
                main_window,
                "Not implemented error",
                f"Cannot upload data from table {table}",
            )
            raise NotImplementedError("Table must be 'scan' or 'project'.")


class UploadData(QAction):
    def __init__(self, main_window: MainWindow) -> None:
        """Upload data to the server."""

        icon = main_window.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        super().__init__(icon, "Upload data", main_window)
        self.setShortcut("Ctrl+U")
        self.setToolTip("Upload selected data to the server.")
        self.triggered.connect(lambda: upload(main_window))
