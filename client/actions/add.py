# type: ignore[attr-defined]  # See below for why this is needed.
"""Add to library dialogue."""

from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QStyle

from client.widgets.dialogue import AddToLibrary, handle_common_exc
from client.widgets.main_window import MainWindow


class AddData(QAction):
    """Add data to library action."""

    @handle_common_exc
    def _add_to_lib(self: AddData) -> None:
        """Download action creates an add to library dialogue."""
        # FIXME: mypy thinks parent is QObject, not MainWindow; triggers attr-defined.
        if self.parent().table_view.selectionModel().selectedRows():
            match self.parent().current_table():
                case "project":
                    prj_id = self.parent().get_value_from_row(0)
                    AddToLibrary(
                        self.parent().conn_str, None, prj_id, parent=self.parent()
                    )
                case "scan":
                    scan_id = self.parent().get_value_from_row(0)
                    prj_id = self.parent().get_value_from_row(1)
                    AddToLibrary(
                        self.parent().conn_str, scan_id, prj_id, parent=self.parent()
                    )
                case _:
                    AddToLibrary(
                        self.parent().conn_str, None, None, parent=self.parent()
                    )
        else:
            AddToLibrary(self.parent().conn_str, None, None, parent=self.parent())

    def __init__(self: AddData, main_window: MainWindow) -> None:
        """Add data to library action."""
        if not isinstance(main_window, MainWindow):
            msg = f"Parent must be MainWindow, not {type(self.parent())}"
            raise NotImplementedError(msg)
        icon = main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogNewFolder
        )
        super().__init__(icon, "Add data to library", parent=main_window)
        self.setShortcut("Ctrl+Shift+A")
        self.setToolTip("Add data to library/")
        self.triggered.connect(self._add_to_lib)
