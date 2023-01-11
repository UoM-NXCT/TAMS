"""
Add to library dialogue.
"""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QStyle

from client.widgets.dialogue import handle_common_exc

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


class AddData(QAction):
    @handle_common_exc
    def _add_to_library(self) -> None:
        """Download action returns a dialogue with a save scans runner."""
        # TODO: Complete
        # Get the selected table
        table: str = self.parent().current_table()

        if not self.parent().table_view.selectionModel().selectedRows():
            raise ValueError("No row selected.")

        match table:
            case "scan":
                # Get the selected scan
                scan_id: int = self.parent().get_value_from_row(0)
                # Get the selected project
                prj_id: int = self.parent().get_value_from_row(1)
                print(f"Scan ID: {scan_id}, Project ID: {prj_id}")

            case _:
                # Fallback case for when no valid table is selected
                QMessageBox.critical(
                    self.parent(),
                    "Not implemented error",
                    (
                        f"Cannot add to table {table}. The add to library action can"
                        " only add scans. Please select a scan."
                    ),
                )
                raise NotImplementedError("Table must be 'scan'.")

    def __init__(self, main_window: MainWindow) -> None:
        """Add data to library action."""

        icon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogNewFolder
        )
        super().__init__(icon, "Add data to library", main_window)
        self.setShortcut("Ctrl+Shift+A")
        self.setToolTip("Add data to library/")
        self.triggered.connect(self._add_to_library)
