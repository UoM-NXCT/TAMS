"""
Add to library dialogue.
"""

from __future__ import annotations

import typing

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QStyle

from client.widgets.dialogue import AddToLibrary, handle_common_exc

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


class AddData(QAction):
    @handle_common_exc
    def _add_to_lib(self) -> None:
        """Download action creates an add to library dialogue."""

        if self.parent().table_view.selectionModel().selectedRows():
            match self.parent().current_table():
                case "project":
                    prj_id: int = self.parent().get_value_from_row(0)
                    AddToLibrary(None, prj_id, parent=self.parent())
                case "scan":
                    scan_id: int = self.parent().get_value_from_row(0)
                    prj_id: int = self.parent().get_value_from_row(1)
                    AddToLibrary(scan_id, prj_id, parent=self.parent())
                case _:
                    AddToLibrary(None, None, parent=self.parent())
        else:
            AddToLibrary(None, None, parent=self.parent())

    def __init__(self, main_window: MainWindow) -> None:
        """Add data to library action."""

        icon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogNewFolder
        )
        super().__init__(icon, "Add data to library", main_window)
        self.setShortcut("Ctrl+Shift+A")
        self.setToolTip("Add data to library/")
        self.triggered.connect(self._add_to_lib)
