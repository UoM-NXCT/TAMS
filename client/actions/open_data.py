"""Create open download dialogue."""

from __future__ import annotations

import errno
import os
import typing
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import QMessageBox, QStyle

from client import settings
from client.widgets.dialogue import handle_common_exc

if typing.TYPE_CHECKING:
    from client.widgets.main_window import MainWindow


class OpenData(QAction):
    """Open data in local library."""

    @handle_common_exc
    def _open_data(self: OpenData) -> None:
        """Open directory in local library.

        Runs when the action is triggered.
        """
        local_lib_str = settings.get_lib("local")
        if not local_lib_str:
            msg = "Local library path not set. Please set it in the settings."
            raise RuntimeError(msg)
        local_lib: Path = Path(local_lib_str)

        # Get the selected table
        table = self.parent().current_table()
        match table:
            case "scan":
                # Get the selected scan
                scan_id = self.parent().get_value_from_row(0)
                prj_id = self.parent().get_value_from_row(1)
                scan_path = local_lib / str(prj_id) / str(scan_id)
                if not scan_path.exists():
                    raise FileNotFoundError(
                        errno.ENOENT, os.strerror(errno.ENOENT), scan_path
                    )
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(scan_path)))
            case "project":
                # Get the selected project
                prj_id = self.parent().get_value_from_row(0)
                prj_path = local_lib / str(prj_id)
                if not prj_path.exists():
                    raise FileNotFoundError(
                        errno.ENOENT, os.strerror(errno.ENOENT), prj_path
                    )
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(prj_path)))
            case _:
                msg = f"Cannot download data from table {table}."
                QMessageBox.critical(self.parent(), "Not implemented error", msg)
                raise RuntimeError(msg)

    def __init__(self: OpenData, main_window: MainWindow) -> None:
        """Open data action."""
        icon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogOpenButton
        )
        super().__init__(icon, "Open data", main_window)
        self.setShortcut("Ctrl+O")
        self.setToolTip("Open selected data in the local library.")
        self.triggered.connect(self._open_data)
