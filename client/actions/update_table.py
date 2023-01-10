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


def update_table(main_window: MainWindow) -> None:
    """Update table model using SQL command."""

    # Get table data
    select_value, from_value, where_value = main_window.current_table_query
    if main_window.db_view:
        if where_value:
            data, column_headers = main_window.db_view.view_select_from_where(
                select_value, from_value, where_value
            )
        else:
            data, column_headers = main_window.db_view.view_select_from_where(
                select_value, from_value
            )
    else:
        data = []
        column_headers = ()

    # Create table model
    main_window.table_model = TableModel(data, column_headers)

    # Create proxy model
    main_window.proxy_model = QSortFilterProxyModel()

    # Set proxy model to table model
    main_window.proxy_model.setSourceModel(main_window.table_model)

    # Make the filters case-insensitive
    main_window.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    # Connect search query to proxy model
    # Note: must do this on each table update, or it will disconnect
    main_window.search.textChanged.connect(main_window.proxy_model.setFilterFixedString)

    # Filter by all columns
    main_window.proxy_model.setFilterKeyColumn(-1)

    # Set the table view to use the proxy model
    main_window.table_view.setModel(main_window.proxy_model)

    # Make table look pretty

    # Stretch table to fill window and store width of each column
    main_window.table_view.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.ResizeToContents
    )
    header_widths = tuple(
        main_window.table_view.horizontalHeader().sectionSize(i)
        for i, _ in enumerate(column_headers)
    )

    # Set the width of each column to be interactive for the user
    main_window.table_view.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.Interactive
    )

    # Set initial width of each column to be the width of the header when pretty
    for i, width in enumerate(header_widths):
        main_window.table_view.horizontalHeader().resizeSection(i, width)

    # Make the table react to selection changes
    main_window.table_view.selectionModel().selectionChanged.connect(
        main_window.on_selection_changed
    )

    # Let user sort table by column
    main_window.table_view.setSortingEnabled(True)

    # Update metadata panel
    main_window.metadata_panel.update_metadata()


def update_table_with_projects(main_window: MainWindow) -> None:
    """Update table to display projects."""

    main_window.current_table_query = (
        "project_id, title, start_date, end_date",
        "project",
        None,
    )
    main_window.update_table_act.trigger()


def update_table_with_scans(main_window: MainWindow) -> None:
    """Update the table widget to display scans."""

    main_window.current_table_query = (
        "scan_id, project_id, instrument_id",
        "scan",
        None,
    )
    main_window.update_table_act.trigger()


def update_table_with_users(main_window: MainWindow) -> None:
    """Update the table widget to display users."""

    main_window.current_table_query = (
        "user_id, first_name, last_name, email_address",
        '"user"',
        None,
    )
    main_window.update_table_act.trigger()


class UpdateTable(QAction):
    def __init__(self, main_window: MainWindow) -> None:
        """Update table action."""

        icon = main_window.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        super().__init__(icon, "Reload table")
        self.setShortcut("Ctrl+R")
        self.setToolTip("Reload the table currently being displayed.")
        self.triggered.connect(lambda: update_table(main_window))
