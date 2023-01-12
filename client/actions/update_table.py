"""
Update the table in the main window.
"""

from __future__ import annotations

import typing

from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QHeaderView, QStyle

from client.widgets.table import TableModel

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


class UpdateTable(QAction):
    def _on_selection_change(self):
        """Update the metadata when a new row is selected.

        This method is called when the selection in the table changes.
        """

        # Get the primary key from the first column (assume first column is the pk)
        key: int = self.parent().selected_row()[0]

        # Each item has a different metadata format; use the current table to method
        metadata: tuple[tuple[any], list[str]]
        if self.parent().current_table() == "project":
            metadata = self.parent().db_view.get_project_metadata(key)
        elif self.current_table() == "scan":
            metadata = self.parent().db_view.get_scan_metadata(key)
        elif self.current_table() == '"user"':
            metadata = self.parent().db_view.get_user_metadata(key)
        else:
            raise NotImplementedError(f"Unknown table {self.parent().current_table()}")

        # Update the metadata panel with the new metadata
        self.parent().metadata_panel.update_metadata(metadata)

    def _update_table(self) -> None:
        """Update table model using SQL command.

        This method is called when the action is triggered.
        """

        # Get table data
        sel_val, from_val, where_val = self.parent().current_table_query
        if self.parent().db_view:
            if where_val:
                data, col_headers = self.parent().db_view.view_select_from_where(
                    sel_val, from_val, where_val
                )
            else:
                data, col_headers = self.parent().db_view.view_select_from_where(
                    sel_val, from_val
                )
        else:
            data = []
            col_headers = ()

        # Create table model
        self.parent().table_model = TableModel(data, col_headers)

        # Create proxy model
        self.parent().proxy_model = QSortFilterProxyModel()

        # Set proxy model to table model
        self.parent().proxy_model.setSourceModel(self.parent().table_model)

        # Make the filters case-insensitive
        self.parent().proxy_model.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        # Connect search query to proxy model
        # Note: must do this on each table update, or it will disconnect
        self.parent().search.textChanged.connect(
            self.parent().proxy_model.setFilterFixedString
        )

        # Filter by all columns
        self.parent().proxy_model.setFilterKeyColumn(-1)

        # Set the table view to use the proxy model
        self.parent().table_view.setModel(self.parent().proxy_model)

        # Make table look pretty
        self.parent().table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header_widths = tuple(
            self.parent().table_view.horizontalHeader().sectionSize(i)
            for i, _ in enumerate(col_headers)
        )
        self.parent().table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        for i, width in enumerate(header_widths):
            self.parent().table_view.horizontalHeader().resizeSection(i, width)

        # Make the table react to selection changes
        self.parent().table_view.selectionModel().selectionChanged.connect(
            self._on_selection_change
        )

        # Let user sort table by column
        self.parent().table_view.setSortingEnabled(True)

        # Update metadata panel
        self.parent().metadata_panel.update_metadata()

    def __init__(self, main_window: MainWindow) -> None:
        """Update table action."""

        icon = main_window.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        super().__init__(icon, "Reload table", main_window)
        self.setShortcut("Ctrl+R")
        self.setToolTip("Reload the table currently being displayed.")
        self.triggered.connect(self._update_table)  # Runs on self.trigger()

    def with_users(self) -> None:
        """Update the table widget to display users."""

        self.parent().current_table_query = (
            "user_id, first_name, last_name, email_address",
            '"user"',
            None,
        )
        self.trigger()

    def with_scans(self) -> None:
        """Update the table widget to display scans."""

        self.parent().current_table_query = (
            "scan_id, project_id, instrument_id",
            "scan",
            None,
        )
        self.trigger()

    def with_projects(self) -> None:
        """Update table to display projects."""

        self.parent().current_table_query = (
            "project_id, title, start_date, end_date",
            "project",
            None,
        )
        self.trigger()
