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
    """Validate action."""

    @handle_common_exc
    def _validate(self: Validate) -> None:
        """Validate action creates a dialogue with a validation runner.

        This method is called when the action is triggered.
        """
        table = self.parent().current_table()
        match table:
            case "scan":
                scan_id = self.parent().get_value_from_row(0)
                prj_id = self.parent().get_value_from_row(1)
                runner = ValidateScans(prj_id, scan_id)
                Validate(runner, parent_widget=self.parent())
            case "project":
                prj_id = self.parent().get_value_from_row(0)
                runner = ValidateScans(prj_id)
                Validate(runner, parent_widget=self.parent())
            case _:
                msg = f"Cannot download data from table {table}."
                QMessageBox.critical(self.parent(), "Not implemented error", msg)
                raise NotImplementedError(msg)

    def __init__(self: Validate, main_window: MainWindow) -> None:
        """Create a new validate action."""
        icon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogContentsView
        )
        super().__init__(icon, "Validate data", main_window)
        self.setShortcut("Ctrl+V")
        self.setToolTip("Validate selected data")
        self.triggered.connect(self._validate)
