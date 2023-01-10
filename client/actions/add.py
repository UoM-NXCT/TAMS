"""
Add to library dialogue.
"""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QStyle

from client.runners import SaveScans
from client.widgets.dialogue import DownloadScans, handle_common_exc

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


@handle_common_exc
def add_to_library(main_window: MainWindow) -> None:
    """Download action returns a dialogue with a save scans runner."""

    # Get the selected table
    table: str = main_window.current_table()

    if not main_window.table_view.selectionModel().selectedRows():
        raise ValueError("No row selected.")

    match table:
        case "scan":
            # Get the selected scan
            scan_id: int = main_window.get_value_from_row(0)
            # Get the selected project
            prj_id: int = main_window.get_value_from_row(1)
            print(f"Scan ID: {scan_id}, Project ID: {prj_id}")

        case _:
            # Fallback case for when no valid table is selected
            QMessageBox.critical(
                main_window,
                "Not implemented error",
                (
                    f"Cannot add to table {table}. The add to library action can only"
                    " add scans. Please select a scan."
                ),
            )
            raise NotImplementedError("Table must be 'scan'.")


class AddData(QAction):
    def __init__(self, main_window: MainWindow) -> None:
        """Add data to library action."""

        icon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogNewFolder
        )
        super().__init__(icon, "Add data to library", main_window)
        self.setShortcut("Ctrl+Shift+A")
        self.setToolTip("Add data to library/")
        self.triggered.connect(lambda: add_to_library(main_window))
