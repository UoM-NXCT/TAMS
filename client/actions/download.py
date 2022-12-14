"""
Create file download dialogue.
"""

from __future__ import annotations

import typing

from PySide6.QtWidgets import QMessageBox

from client.runners import SaveScans
from client.widgets.dialogue import DownloadScans, handle_common_exc

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


@handle_common_exc
def download(main_window: MainWindow) -> DownloadScans:
    """Download action returns a dialogue with a save scans runner."""

    # Get the selected table
    table: str = main_window.current_table()

    match table:
        case "scan":
            # Get the selected scan
            scan_id: int = main_window.get_value_from_row(0)
            prj_id: int = main_window.get_value_from_row(1)

            # Return the scan download dialogue
            runner: SaveScans = SaveScans(prj_id, scan_id, download=True)
            return DownloadScans(runner, parent_widget=main_window)

        case "project":
            # Get the selected project
            prj_id = main_window.get_value_from_row(0)

            # Return the project download dialogue
            runner = SaveScans(prj_id, download=True)
            return DownloadScans(runner, parent_widget=main_window)

        case _:
            # Fallback case for when no valid table is selected
            QMessageBox.critical(
                main_window,
                "Not implemented error",
                f"Cannot download data from table {table}",
            )
            raise NotImplementedError("Table must be 'scan' or 'project'.")
