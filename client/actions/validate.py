"""
Create file validation dialogue.
"""

from __future__ import annotations

import typing

from PySide6.QtWidgets import QDialog, QMessageBox

from client.runners import ValidateScans
from client.widgets.dialogue import Validate, attempt_file_io

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


@attempt_file_io
def validate(main_window: MainWindow) -> QDialog:
    """Validate action returns a dialogue with a validation runner."""

    # Get the selected table
    table: str = main_window.current_table()

    match table:
        case "scan":
            # Get the selected scan
            scan_id: int = main_window.get_value_from_row(0)
            prj_id: int = main_window.get_value_from_row(1)

            # Return the scan validation dialogue
            runner: ValidateScans = ValidateScans(prj_id, scan_id)
            return Validate(runner, parent_widget=main_window)

        case "project":
            # Get the selected project
            prj_id = main_window.get_value_from_row(0)

            # Return the project validation dialogue
            runner = ValidateScans(prj_id)
            return Validate(runner, parent_widget=main_window)

        case _:
            # Fallback case for when no valid table is selected
            QMessageBox.critical(
                main_window,
                "Not implemented error",
                f"Cannot download data from table {table}",
            )
            raise NotImplementedError("Table must be 'scan' or 'project'.")
