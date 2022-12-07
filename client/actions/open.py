"""
Create open download dialogue.
"""

from __future__ import annotations

import errno
import os
import typing
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox

from client import settings
from client.widgets.dialogue import handle_common_exc

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


@handle_common_exc
def open_data(main_window: MainWindow) -> None:
    """Open directory in local library."""

    # Get the path of the local library
    local_lib_str: str = settings.get_lib("local")
    if not local_lib_str:
        raise RuntimeError("Local library path not set")
    local_lib: Path = Path(local_lib_str)

    # Get the selected table
    table: str = main_window.current_table()

    match table:
        case "scan":
            # Get the selected scan
            scan_id: int = main_window.get_value_from_row(0)
            prj_id: int = main_window.get_value_from_row(1)
            scan_path: Path = local_lib / str(prj_id) / str(scan_id)
            if not scan_path.exists():
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), scan_path
                )
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(scan_path)))

        case "project":
            # Get the selected project
            prj_id = main_window.get_value_from_row(0)
            prj_path: Path = local_lib / str(prj_id)
            if not prj_path.exists():
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), prj_path
                )
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(prj_path)))

        case _:
            # Fallback case for when no valid table is selected
            QMessageBox.critical(
                main_window,
                "Not implemented error",
                f"Cannot download data from table {table}",
            )
            raise RuntimeError("Table must be 'scan' or 'project'.")
