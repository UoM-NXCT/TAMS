"""
Main window for the GUI.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QModelIndex, QSize, QSortFilterProxyModel, Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QGridLayout,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from client import actions, settings
from client.db import DatabaseView
from client.runners import SaveScans, ValidateScans
from client.utils import log
from client.widgets.dialogue import (
    About,
    CreatePrj,
    CreateScan,
    DownloadScans,
    Login,
    Settings,
    UploadScans,
    Validate,
    handle_common_exc,
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
        self.create_actions()
        self.create_window()
        self.create_tool_bar()

        self.show()

        actions.update_table(self)

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
        self.update_table_with_projects()

        # Add the table and search query to table layout
        self.table_layout.addWidget(self.search)
        self.table_layout.addWidget(self.table_view)
        table_widget.setLayout(self.table_layout)

        # Create table toolbox
        self.toolbox = ToolBox()

        # Link toolbox buttons to functions
        self.toolbox.prj_btn.clicked.connect(self.update_table_with_projects)
        self.toolbox.create_prj_btn.clicked.connect(
            lambda: CreatePrj(self, self.conn_str)
        )
        self.toolbox.scans_btn.clicked.connect(self.update_table_with_scans)
        self.toolbox.create_scan_btn.clicked.connect(self.open_create_scan)
        self.toolbox.users_btn.clicked.connect(self.update_table_with_users)

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

    def update_table_with_projects(self) -> None:
        """Update table to display projects."""

        self.current_table_query = (
            "project_id, title, start_date, end_date",
            "project",
            None,
        )
        actions.update_table(self)

    def update_table_with_users(self) -> None:
        """Update the table widget to display users."""

        self.current_table_query = (
            "user_id, first_name, last_name, email_address",
            '"user"',
            None,
        )
        actions.update_table(self)

    def update_table_with_scans(self) -> None:
        """Update the table widget to display scans."""

        self.current_table_query = ("scan_id, project_id, instrument_id", "scan", None)
        actions.update_table(self)

    def create_actions(self):
        """Create the application actions."""

        # Create actions for the File menu

        self.settings_act = QAction("Settings")
        self.settings_act.setShortcut("Ctrl+Alt+S")
        self.settings_act.setStatusTip("Edit application settings")
        self.settings_act.triggered.connect(
            lambda: Settings()  # pylint: disable=unnecessary-lambda
        )

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        self.reload_table_act = QAction(icon, "Reload")
        self.reload_table_act.setShortcut("F5")
        self.reload_table_act.setToolTip("Reload the active table")
        self.reload_table_act.triggered.connect(lambda: actions.update_table(self))

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        self.download_act = QAction(icon, "Download data")
        self.download_act.setShortcut("Ctrl+D")
        self.download_act.setToolTip("Download selected data")
        self.download_act.triggered.connect(lambda: actions.download(self))

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        self.upload_act = QAction(icon, "Upload data")
        self.upload_act.setShortcut("Ctrl+U")
        self.upload_act.setToolTip("Upload selected data")
        self.upload_act.triggered.connect(lambda: actions.upload(self))

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        self.open_act = QAction(icon, "Open data")
        self.open_act.setShortcut("Ctrl+O")
        self.open_act.setToolTip("Open selected data")
        self.open_act.triggered.connect(lambda: actions.open_data(self))

        icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogContentsView
        )
        self.validate_act = QAction(icon, "Validate data")
        self.validate_act.setShortcut("Ctrl+V")
        self.validate_act.setToolTip("Validate selected data")
        self.validate_act.triggered.connect(lambda: actions.validate(self))

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
        self.add_act = QAction(icon, "Add data")
        self.add_act.setShortcut("Ctrl+A")
        self.add_act.setToolTip("Add data to the local library")
        self.add_act.triggered.connect(lambda: print("Add data"))

        self.quit_act = QAction("&Quit")
        self.quit_act.setShortcut("Ctrl+Q")
        self.quit_act.setStatusTip("Quit application")
        self.quit_act.triggered.connect(self.close)  # close is a method of QMainWindow

        # Create actions for the View menu

        self.full_screen_act = QAction("Full Screen", checkable=True)
        self.full_screen_act.setStatusTip("Toggle full screen mode")
        self.full_screen_act.triggered.connect(
            lambda: actions.toggle_full_screen(self, self.full_screen_act.isChecked())
        )

        # Create actions for the Help menu

        self.doc_act = QAction("Documentation")
        self.doc_act.setShortcut("F1")
        self.doc_act.setStatusTip("Open documentation in browser")
        self.doc_act.triggered.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://tams-nxct.readthedocs.io/")
            )  # pylint: disable=unnecessary-lambda
        )

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        self.about_act = QAction(icon, "About")
        self.about_act.setStatusTip("Show information about this software")
        self.about_act.triggered.connect(
            lambda: About()  # pylint: disable=unnecessary-lambda
        )

    def open_create_scan(self) -> None:
        """
        Open the scan creation dialogue; pass the database connection string so that
        the window can access the database.
        """

        self.create_scan_dlg = CreateScan(self.conn_str)

    def create_window(self):
        """Create the application menu bar."""

        # Due to macOS guidelines, the menu bar will not appear in the GUI.
        self.menuBar().setNativeMenuBar(True)

        # Create the File menu
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.settings_act)
        file_menu.addAction(self.reload_table_act)
        file_menu.addSeparator()
        file_menu.addAction(self.download_act)
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
        toolbar.addAction(self.reload_table_act)
        toolbar.addAction(self.download_act)
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

    def on_selection_changed(self) -> None:
        """Update the metadata when a new row is selected."""

        # Because the rows can be sorted, the Nth item in the visible table may not be the Nth item in data
        # Hence, we have to translate the visible index to the source index
        proxy_index: QModelIndex = self.table_view.currentIndex()
        source_index: QModelIndex = self.proxy_model.mapToSource(proxy_index)

        # We care about the row, so get the row from the current index
        row_index: int = source_index.row()
        row: tuple[Any] = self.table_model.get_row_data(row_index)

        # Get the primary key from the first column (assume first column is the pk)
        key: int = row[0]

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
