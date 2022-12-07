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
    attempt_file_io,
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
        self.create_prj: QWidget
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

        self.update_table()

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
        self.table_view.doubleClicked.connect(lambda: self.open_data())
        self.update_table_with_projects()

        # Add the table and search query to table layout
        self.table_layout.addWidget(self.search)
        self.table_layout.addWidget(self.table_view)
        table_widget.setLayout(self.table_layout)

        # Create table toolbox
        self.toolbox = ToolBox()

        # Link toolbox buttons to functions
        self.toolbox.prj_btn.clicked.connect(self.update_table_with_projects)
        self.toolbox.create_prj_btn.clicked.connect(self.open_create_prj)
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

    def update_table(self) -> None:
        """Update table model using SQL command."""

        # Get table data
        select_value, from_value, where_value = self.current_table_query
        if self.db_view:
            if where_value:
                data, column_headers = self.db_view.view_select_from_where(
                    select_value, from_value, where_value
                )
            else:
                data, column_headers = self.db_view.view_select_from_where(
                    select_value, from_value
                )
        else:
            data = []
            column_headers = ()

        # Create table model
        self.table_model = TableModel(data, column_headers)

        # Create proxy model
        self.proxy_model = QSortFilterProxyModel()

        # Set proxy model to table model
        self.proxy_model.setSourceModel(self.table_model)

        # Make the filters case-insensitive
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        # Connect search query to proxy model
        # Note: must do this on each table update, or it will disconnect
        self.search.textChanged.connect(self.proxy_model.setFilterFixedString)

        # Filter by all columns
        self.proxy_model.setFilterKeyColumn(-1)

        # Set the table view to use the proxy model
        self.table_view.setModel(self.proxy_model)

        # Make table look pretty

        # Stretch table to fill window and store width of each column
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header_widths = tuple(
            self.table_view.horizontalHeader().sectionSize(i)
            for i, _ in enumerate(column_headers)
        )

        # Set the width of each column to be interactive for the user
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )

        # Set initial width of each column to be the width of the header when pretty
        for i, width in enumerate(header_widths):
            self.table_view.horizontalHeader().resizeSection(i, width)

        # Make the table react to selection changes
        self.table_view.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        # Let user sort table by column
        self.table_view.setSortingEnabled(True)

        # Update metadata panel
        self.metadata_panel.update_metadata()

    def update_table_with_projects(self) -> None:
        """Update table to display projects."""

        self.current_table_query = (
            "project_id, title, start_date, end_date",
            "project",
            None,
        )
        self.update_table()

    def update_table_with_users(self) -> None:
        """Update the table widget to display users."""

        self.current_table_query = (
            "user_id, first_name, last_name, email_address",
            '"user"',
            None,
        )
        self.update_table()

    def update_table_with_scans(self) -> None:
        """Update the table widget to display scans."""

        self.current_table_query = ("scan_id, project_id, instrument_id", "scan", None)
        self.update_table()

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
        self.reload_table_act.triggered.connect(self.update_table)

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        self.download_act = QAction(icon, "Download data")
        self.download_act.setShortcut("Ctrl+D")
        self.download_act.setToolTip("Download selected data")
        self.download_act.triggered.connect(self.download_data)

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        self.upload_act = QAction(icon, "Upload data")
        self.upload_act.setShortcut("Ctrl+U")
        self.upload_act.setToolTip("Upload selected data")
        self.upload_act.triggered.connect(self.upload_data)

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        self.open_act = QAction(icon, "Open data")
        self.open_act.setShortcut("Ctrl+O")
        self.open_act.setToolTip("Open selected data")
        self.open_act.triggered.connect(self.open_data)

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
        self.add_act.triggered.connect(self.add_data)

        self.quit_act = QAction("&Quit")
        self.quit_act.setShortcut("Ctrl+Q")
        self.quit_act.setStatusTip("Quit application")
        self.quit_act.triggered.connect(self.close)

        # Create actions for the View menu

        self.full_screen_act = QAction("Full Screen", checkable=True)
        self.full_screen_act.setStatusTip("Toggle full screen mode")
        self.full_screen_act.triggered.connect(self.toggle_full_screen)

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

    def toggle_full_screen(self, state) -> None:
        """Toggle full screen mode."""

        if state:
            self.showFullScreen()
        else:
            self.showNormal()

    def open_create_prj(self) -> None:
        """
        Open the create project window; pass the database connection string so that
        the window can access the database.
        """

        self.create_prj = CreatePrj(self.conn_str)

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

    @attempt_file_io
    def upload_data(self) -> None:
        """Upload data to the database."""

        # Get the selected table
        table = self.current_table()

        # Get the primary key of the selected row
        row_pk: int = self.get_value_from_row(0)

        if table == "project":
            runner = SaveScans(row_pk, download=False)
            self.upload_dlg = UploadScans(runner)
        elif table == "scan":
            prj_id: int = self.get_value_from_row(1)
            runner = SaveScans(prj_id, row_pk, download=False)
            self.upload_dlg = UploadScans(runner)
        else:
            logger.error("Cannot upload data from table %s", table)
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot upload data from table {table}",
            )

    @attempt_file_io
    def download_data(self):
        """Download selected data."""

        # Get the selected table
        table = self.current_table()

        # Get the primary key of the selected row
        row_pk: int = self.get_value_from_row(0)

        if table == "project":
            runner = SaveScans(row_pk, download=True)
            self.download_dlg = DownloadScans(runner)

        elif table == "scan":
            # Get the path of the local scan directory
            prj_id: int = self.get_value_from_row(1)

            runner = SaveScans(prj_id, row_pk, download=True)
            self.download_dlg = DownloadScans(runner)

        else:
            logger.error("Cannot download data from table %s", table)
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot download data from table {table}",
            )

    @attempt_file_io
    def open_data(self) -> None:
        """Open selected data."""

        # Get the selected table
        table = self.current_table()

        # Get the primary key of the selected row
        row_pk: int = self.get_value_from_row(0)

        # Get the path of the local library
        try:
            local_lib: Path = Path(settings.get_lib("local"))
        except TypeError:
            logger.error("Local library path not set")
            QMessageBox.critical(
                self,
                "Error",
                "Local library path not set",
            )
            return

        if table == "project":
            logging.info("Opening data from project ID %s", row_pk)

            # Get the path of the local project directory
            prj_path: Path = local_lib / str(row_pk)

            if prj_path.exists():
                logging.info("Opening project path %s", prj_path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(prj_path)))
            else:
                logging.error("Project path %s does not exist", prj_path)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Project ID {row_pk} does not exist in the local library. Has the "
                    "data been downloaded?",
                )
        elif table == "scan":
            logging.info("Opening data from scan ID %s", row_pk)

            # Get the path of the local scan directory
            project_id: int = self.get_value_from_row(1)
            scan_path: Path = local_lib / str(project_id) / str(row_pk)

            if scan_path.exists():
                logging.info("Opening scan path %s", scan_path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(scan_path)))
            else:
                logging.error("Scan path %s does not exist", scan_path)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Scan ID {row_pk} does not exist in the local library. Has the data"
                    " been downloaded?",
                )
        else:
            logging.error("Cannot open data from table %s", table)
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot open data from table {table}",
            )

    @attempt_file_io
    def add_data(self) -> None:
        """Add data to the local library."""

        # Get the selected table
        table = self.current_table()

        if table == "project":
            raise NotImplementedError("Adding projects is not yet implemented")
        elif table == "scan":
            print("Adding scan")
        else:
            logging.error("Cannot add data to table %s", table)
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot add data to table {table}",
            )

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
