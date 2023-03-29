"""Create file validation dialogue."""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QStyle

from client.runners import ValidateScans
from client.widgets.dialogue import Validate, handle_common_exc

if typing.TYPE_CHECKING:
    from client.widgets.main_window import MainWindow


class ValidateData(QAction):
    @handle_common_exc
    def _validate(self) -> None:
        """Validate action creates a dialogue with a validation runner.

        This method is called when the action is triggered.
        """
        table: str = self.parent().current_table()

        match table:
            case "scan":
                scan_id: int = self.parent().get_value_from_row(0)
                prj_id: int = self.parent().get_value_from_row(1)
                runner: ValidateScans = ValidateScans(prj_id, scan_id)
                Validate(runner, parent_widget=self.parent())
                return
            case "project":
                prj_id = self.parent().get_value_from_row(0)
                runner = ValidateScans(prj_id)
                Validate(runner, parent_widget=self.parent())
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
        """Create a new validate action."""
        icon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogContentsView
        )
        super().__init__(icon, "Validate data", main_window)
        self.setShortcut("Ctrl+V")
        self.setToolTip("Validate selected data")
        self.triggered.connect(self._validate)
