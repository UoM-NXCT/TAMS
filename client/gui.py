"""
Main window for the GUI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QModelIndex, QSize, QSortFilterProxyModel, Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from client import actions
from client.db import DatabaseView
from client.utils import log
from client.widgets.dialogue import (
    About,
    AddToLibrary,
    CreatePrj,
    CreateScan,
    DownloadScans,
    Login,
    Settings,
)
from client.widgets.metadata_panel import MetadataPanel
from client.widgets.table import TableModel, TableView
from client.widgets.toolbox import ToolBox

TAMS_ROOT = Path(__file__).parents[1]

logger = log.logger(__name__)


class MainWindow(QMainWindow):
    """The main Qt window for the database application."""

    def __init__(self):
        super().__init__()

        # Create empty variables for use later.
        self.db_view: DatabaseView | None = None
        self.conn_str: str | None = None
        self.table_model: TableModel | None = None
        self.proxy_model: QSortFilterProxyModel | None = None
        self.current_table_query: tuple | None = None
        self.toolbox: ToolBox | None = None
        self.current_metadata: tuple | None = None

        # Define empty widgets for use later
        self.settings_dlg: QWidget
        self.create_scan_dlg: QWidget
        self.download_dlg: DownloadScans

        # Set up the application's GUI.
        self.setMinimumSize(1080, 720)
        self.setWindowTitle("Tomography Archival Management Software")

        try:
            login_dlg = Login()
            login_dlg.exec()
            self.conn_str = login_dlg.conn_str
            self.db_view = DatabaseView(self.conn_str)
        except SystemExit:
            # User closed the login window
            sys.exit()

        self.set_up_main_window()
        self._create_actions()
        self.create_window()
        self.create_tool_bar()
        actions.update_table_with_projects(self)
        self.show()

        self.update_table_act.trigger()

    def set_up_main_window(self) -> None:
        """Create and arrange widgets in the main window."""

        # Create the status bar
        self.setStatusBar(QStatusBar())

        # Metadata panel
        self.metadata_panel = MetadataPanel()

        # Create table layout
        table_widget = QWidget()
        self.table_layout = QVBoxLayout()

        # Create search query
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search the table...")

        # Create a table; initialize with projects
        self.table_view = TableView()
        self.table_view.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.table_view.doubleClicked.connect(lambda: actions.open_data(self))

        # Add the table and search query to table layout
        self.table_layout.addWidget(self.search)
        self.table_layout.addWidget(self.table_view)
        table_widget.setLayout(self.table_layout)

        # Create table toolbox
        self.toolbox = ToolBox()

        # Link toolbox buttons to functions

        # Project tab buttons
        self.toolbox.prj_btn.clicked.connect(
            lambda: actions.update_table_with_projects(self)
        )
        self.toolbox.create_prj_btn.clicked.connect(
            lambda: CreatePrj(self, self.conn_str)
        )

        # Scan tab buttons
        self.toolbox.scans_btn.clicked.connect(
            lambda: actions.update_table_with_scans(self)
        )
        self.toolbox.create_scan_btn.clicked.connect(
            lambda: CreateScan(self, self.conn_str)
        )

        # User tab buttons
        self.toolbox.users_btn.clicked.connect(
            lambda: actions.update_table_with_users(self)
        )

        # Create layout
        layout: QGridLayout = QGridLayout()
        splitter: QSplitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.toolbox)
        splitter.addWidget(table_widget)
        splitter.addWidget(self.metadata_panel)
        splitter.setSizes([216, 432, 216])  # 1:4 ratio
        layout.addWidget(splitter, 0, 0)

        # Set grid as central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _create_actions(self):
        """Create the application actions.

        Must be called only during initialization (__init__).
        """

        # Create actions for the File menu
        self.settings_act = actions.OpenSettings(self)
        self.update_table_act = actions.UpdateTable(self)
        self.upload_act = actions.UploadData(self)
        self.open_act = actions.OpenData(self)
        self.validate_act = actions.ValidateData(self)
        self.add_act = actions.AddData(self)
        self.quit_act = actions.Quit(self)

        # Create actions for the View menu
        self.full_screen_act = actions.FullScreen(self)

        # Create actions for the Help menu
        self.doc_act = actions.OpenDocs(self)
        self.about_act = actions.OpenAbout(self)

    def create_window(self):
        """Create the application menu bar."""

        # Due to macOS guidelines, the menu bar will not appear in the GUI.
        self.menuBar().setNativeMenuBar(True)

        # Create the File menu
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.settings_act)
        file_menu.addAction(self.update_table_act)
        file_menu.addSeparator()
        # file_menu.addAction(self.download_act)
        file_menu.addAction(self.upload_act)
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.add_act)
        file_menu.addAction(self.validate_act)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_act)

        # Create the View menu
        view_menu = self.menuBar().addMenu("View")
        appearance_submenu = view_menu.addMenu("Appearance")
        appearance_submenu.addAction(self.full_screen_act)

        # Create the Help menu
        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(self.doc_act)
        help_menu.addAction(self.about_act)

    def create_tool_bar(self) -> None:
        """Create the application toolbar."""

        toolbar: QToolBar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Add actions to the toolbar

        # File actions
        toolbar.addAction(self.update_table_act)
        # toolbar.addAction(self.download_act)
        toolbar.addAction(self.upload_act)
        toolbar.addAction(self.add_act)
        toolbar.addAction(self.open_act)
        toolbar.addAction(self.validate_act)

        # Help actions
        toolbar.addSeparator()
        toolbar.addAction(self.about_act)

    def get_value_from_row(self, column: int) -> int:
        """Get the primary key of the selected row in the table view.

        :param column: the column number of the value.
        """

        # Rows can be sorted, so the Nth table item may not be the Nth item in data
        # Hence, we have to translate the visible index to the source index
        proxy_index: QModelIndex = self.table_view.currentIndex()
        source_index: QModelIndex = self.proxy_model.mapToSource(proxy_index)

        # We care about the row, so get the row from the current index
        row_index: int = source_index.row()
        row: tuple[Any] = self.table_model.get_row_data(row_index)
        row_value = row[column]

        return row_value

    def current_table(self) -> str:
        """Get the current table displayed."""

        return self.current_table_query[1]

    def selected_row(self) -> tuple[Any, ...]:
        """Get the selected row in the table view."""

        # Rows can be sorted, so the Nth table item may not be the Nth item in data
        # Hence, we have to translate the visible index to the source index
        proxy_index: QModelIndex = self.table_view.currentIndex()
        source_index: QModelIndex = self.proxy_model.mapToSource(proxy_index)

        # We care about the row, so get the row from the current index
        row_index: int = source_index.row()
        row: tuple[Any] = self.table_model.get_row_data(row_index)

        return row

    def on_selection_changed(self) -> None:
        """Update the metadata when a new row is selected."""

        # Get the primary key from the first column (assume first column is the pk)
        key: int = self.selected_row()[0]

        # Each item has a different metadata format; use the current table to method
        metadata: tuple[tuple[any], list[str]]
        if self.current_table() == "project":
            metadata = self.db_view.get_project_metadata(key)
        elif self.current_table() == "scan":
            metadata = self.db_view.get_scan_metadata(key)
        elif self.current_table() == '"user"':
            metadata = self.db_view.get_user_metadata(key)
        else:
            raise NotImplementedError(f"Unknown table {self.current_table()}")

        # Update the metadata panel with the new metadata
        self.metadata_panel.update_metadata(metadata)
