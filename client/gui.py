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
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QStyle,
    QToolBar,
    QWidget,
)

from client import settings
from client.db import DatabaseView
from client.runners import SaveScans, ValidateScans
from client.utils.toml import load_toml
from client.widgets.dialogue import (
    CreatePrj,
    CreateScan,
    DownloadScans,
    Login,
    Settings,
    UploadScans,
    Validate,
    attempt_file_io,
)
from client.widgets.dialogue.about import About
from client.widgets.metadata_panel import MetadataPanel
from client.widgets.table import TableModel, TableView
from client.widgets.toolbox import ToolBox

TAMS_ROOT = Path(__file__).parents[1]


class MainWindow(QMainWindow):
    """The main Qt window for the database application."""

    def __init__(self):
        super().__init__()

        # Create empty variables for use later.
        self.database_view: DatabaseView | None = None
        self.connection_string: str | None = None
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
            self.connection_string = login_dlg.conn_str
            self.database_view = DatabaseView(self.connection_string)
        except SystemExit:
            sys.exit()

        self.set_up_main_window()
        self.create_actions()
        self.create_window()
        self.create_tool_bar()

        self.show()

    def set_up_main_window(self) -> None:
        """Create and arrange widgets in the main window."""

        # Create the status bar
        self.setStatusBar(QStatusBar())

        # Metadata panel
        self.metadata_panel = MetadataPanel()

        # Create a table; initialize with projects
        self.table_view = TableView()
        self.table_view.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.update_table_with_projects()

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
        splitter.addWidget(self.table_view)
        splitter.addWidget(self.metadata_panel)
        splitter.setSizes([216, 432, 216])  # 1:4 ratio
        layout.addWidget(splitter, 0, 0)

        # Set grid as central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_table(self) -> None:
        """Update table model using SQL command."""

        select_value, from_value, where_value = self.current_table_query
        if self.database_view:
            if where_value:
                data, column_headers = self.database_view.view_select_from_where(
                    select_value, from_value, where_value
                )
            else:
                data, column_headers = self.database_view.view_select_from_where(
                    select_value, from_value
                )
        else:
            data = []
            column_headers = ()
        self.table_model = TableModel(data, column_headers)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)

        # Make table look pretty
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

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
        """Create the application's menu actions."""

        # Create actions for the File menu

        self.settings_act = QAction("Settings")
        self.settings_act.setShortcut("Ctrl+Alt+S")
        self.settings_act.setStatusTip("Edit application settings")
        self.settings_act.triggered.connect(
            lambda: Settings()  # pylint: disable=unnecessary-lambda
        )

        pixmap = QStyle.StandardPixmap.SP_BrowserReload
        reload_table_icon = self.style().standardIcon(pixmap)
        self.reload_table_act = QAction(reload_table_icon, "Reload")
        self.reload_table_act.setShortcut("F5")
        self.reload_table_act.setToolTip("Reload the active table")
        self.reload_table_act.triggered.connect(self.update_table)

        pixmap = QStyle.StandardPixmap.SP_ArrowDown
        download_icon = self.style().standardIcon(pixmap)
        self.download_act = QAction(download_icon, "Download data")
        self.download_act.setShortcut("Ctrl+D")
        self.download_act.setToolTip("Download selected data")
        self.download_act.triggered.connect(self.download_data)

        pixmap = QStyle.StandardPixmap.SP_ArrowUp
        upload_icon = self.style().standardIcon(pixmap)
        self.upload_act = QAction(upload_icon, "Upload data")
        self.upload_act.setShortcut("Ctrl+U")
        self.upload_act.setToolTip("Upload selected data")
        self.upload_act.triggered.connect(self.upload_data)

        pixmap = QStyle.StandardPixmap.SP_DialogOpenButton
        open_icon = self.style().standardIcon(pixmap)
        self.open_act = QAction(open_icon, "Open data")
        self.open_act.setShortcut("Ctrl+O")
        self.open_act.setToolTip("Open selected data")
        self.open_act.triggered.connect(self.open_data)

        pixmap = QStyle.StandardPixmap.SP_FileDialogContentsView
        validate_icon = self.style().standardIcon(pixmap)
        self.validate_act = QAction(validate_icon, "Validate data")
        self.validate_act.setShortcut("Ctrl+V")
        self.validate_act.setToolTip("Validate selected data")
        self.validate_act.triggered.connect(self.validate_data)

        self.quit_act = QAction("&Quit")
        self.quit_act.setShortcut("Ctrl+Q")
        self.quit_act.setStatusTip("Quit application")
        self.quit_act.triggered.connect(self.close)

        # Create actions for the View menu

        self.full_screen_act = QAction("Full Screen", checkable=True)
        self.full_screen_act.setStatusTip("Toggle full screen mode")
        self.full_screen_act.triggered.connect(self.toggle_full_screen)

        # Create actions for the Help menu

        pixmap = QStyle.StandardPixmap.SP_MessageBoxInformation
        about_icon = self.style().standardIcon(pixmap)
        self.about_act = QAction(about_icon, "About")
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

        self.create_prj = CreatePrj(self.connection_string)

    def open_create_scan(self) -> None:
        """
        Open the scan creation dialogue; pass the database connection string so that
        the window can access the database.
        """

        self.create_scan_dlg = CreateScan(self.connection_string)

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
        file_menu.addAction(self.validate_act)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_act)

        # Create the View menu
        view_menu = self.menuBar().addMenu("View")
        appearance_submenu = view_menu.addMenu("Appearance")
        appearance_submenu.addAction(self.full_screen_act)

        # Create the Help menu
        help_menu = self.menuBar().addMenu("Help")
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
        toolbar.addAction(self.open_act)
        toolbar.addAction(self.validate_act)

        # Config actions
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
            logging.info("Uploading data from project ID %s", row_pk)
            runner = SaveScans(row_pk, download=False)
            self.upload_dlg = UploadScans(runner)
        elif table == "scan":
            logging.info("Uploading data from scan ID %s", row_pk)
            prj_id: int = self.get_value_from_row(1)
            runner = SaveScans(prj_id, row_pk, download=False)
            self.upload_dlg = UploadScans(runner)
        else:
            logging.error("Cannot upload data from table %s", table)
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
            logging.info("Downloading data from project ID %s", row_pk)

            runner = SaveScans(row_pk, download=True)
            self.download_dlg = DownloadScans(runner)

        elif table == "scan":
            logging.info("Downloading data from scan ID %s", row_pk)

            # Get the path of the local scan directory
            prj_id: int = self.get_value_from_row(1)

            runner = SaveScans(prj_id, row_pk, download=True)
            self.download_dlg = DownloadScans(runner)

        else:
            logging.error("Cannot download data from table %s", table)
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
        local_library: str = load_toml(settings.general)["storage"]["local_library"]

        if table == "project":
            logging.info("Opening data from project ID %s", row_pk)

            # Get the path of the local project directory
            project_path: Path = Path(local_library) / str(row_pk)

            if project_path.exists():
                logging.info("Opening project path %s", project_path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(project_path)))
            else:
                logging.error("Project path %s does not exist", project_path)
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
            scan_path: Path = Path(local_library) / str(project_id) / str(row_pk)

            if scan_path.exists():
                logging.info("Opening scan path %s", scan_path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(scan_path)))
            else:
                logging.error("Scan path %s does not exist", scan_path)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Scan ID {row_pk} does not exist in the local library. Has the data been downloaded?",
                )
        else:
            logging.error("Cannot open data from table %s", table)
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot open data from table {table}",
            )

    @attempt_file_io
    def validate_data(self):
        """Download selected data."""

        # Get the selected table
        table = self.current_table()

        # Get the primary key of the selected row
        row_pk: int = self.get_value_from_row(0)

        if table == "project":
            logging.info("Validating data from project ID %s", row_pk)

            runner = ValidateScans(row_pk)
            self.download_dlg = Validate(runner)

        elif table == "scan":
            logging.info("Validating data from scan ID %s", row_pk)

            # Get the path of the local scan directory
            project_id: int = self.get_value_from_row(1)

            runner = ValidateScans(project_id, row_pk)
            self.download_dlg = Validate(runner)

        else:
            logging.error("Cannot validate.py data from table %s", table)
            QMessageBox.critical(
                self,
                "Error",
                f"Cannot download data from table {table}",
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
            metadata = self.database_view.get_project_metadata(key)
        elif self.current_table() == "scan":
            metadata = self.database_view.get_scan_metadata(key)
        elif self.current_table() == '"user"':
            metadata = self.database_view.get_user_metadata(key)
        else:
            # Escape the function if not a valid table
            logging.warning("%s is not a valid table.", self.current_table())
            return

        # Update the metadata panel with the new metadata
        self.metadata_panel.update_metadata(metadata)
