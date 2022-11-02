# -*- coding: utf-8 -*-

import logging
import sys
from pathlib import Path

from create_project_dialogue import CreateProjectWindow
from db import DatabaseView, MissingTables, dict_to_conn_str
from metadata_panel import MetadataPanel
from psycopg.errors import ConnectionFailure
from PySide6.QtCore import QModelIndex, QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from settings import toml_operations
from settings_dialogue import SettingsWindow
from table_widget import TableModel, TableView
from toolbox import ToolBox

logging.basicConfig(level=logging.DEBUG)


class MainWindow(QMainWindow):
    """The main Qt window for the database application."""

    def __init__(self):
        super().__init__()

        # Create empty variables for use later.
        self.database_view: DatabaseView | None = None
        self.connection_string: str | None = None
        self.table_model: TableModel | None = None
        self.proxy_table_model: QSortFilterProxyModel | None = None
        self.current_table_query: tuple[str] | None = None
        self.toolbox: ToolBox | None = None
        self.current_metadata: tuple | None = None
        # Create empty windows for use later.
        self.settings: QWidget | None = None
        self.create_project: QWidget | None = None

        self.initialize_ui()

    def initialize_ui(self):
        """Set up the application's GUI."""
        self.setMinimumSize(1080, 720)
        self.setWindowTitle("Untitled Database Application")
        self.connect_to_database()
        self.set_up_main_window()
        self.create_actions()
        self.create_window()
        self.create_tool_bar()

        self.show()

    def update_table(self):
        """Update table model using SQL command."""
        logging.info("Updating table")

        select_value, from_value, where_value = self.current_table_query
        if where_value:
            data, column_headers = self.database_view.view_select_from_where(
                select_value, from_value, where_value
            )
        else:
            data, column_headers = self.database_view.view_select_from_where(
                select_value, from_value
            )
        self.table_model = TableModel(data, column_headers)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.proxy_model)

        # Make table look pretty
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Make the table react to selection changes
        self.table_view.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        # Let user sort table by column
        self.table_view.setSortingEnabled(True)

    def update_table_with_projects(self):
        """Update table to display projects."""

        self.current_table_query = [
            "project_id, title, start_date, end_date",
            "project",
            None,
        ]
        self.update_table()

    def update_table_with_users(self):
        """Update the table widget to display users."""

        self.current_table_query = [
            "user_id, first_name, last_name, email_address",
            '"user"',
            None,
        ]
        self.update_table()

    def update_table_with_scans(self):
        """Update the table widget to display scans."""

        self.current_table_query = ["scan_id, project_id", "scan", None]
        self.update_table()

    def set_up_main_window(self):
        """Create and arrange widgets in the main window."""

        # Create the status bar
        self.setStatusBar(QStatusBar())

        # Create table; initialise with projects
        self.table_view = TableView()
        self.table_view.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.update_table_with_projects()

        # Create table toolbox
        self.toolbox = ToolBox()
        self.toolbox.projects_button.clicked.connect(self.update_table_with_projects)
        self.toolbox.create_project_button.clicked.connect(self.open_create_project)
        self.toolbox.scans_button.clicked.connect(self.update_table_with_scans)
        self.toolbox.users_button.clicked.connect(self.update_table_with_users)

        # Metadata panel
        self.metadata_panel = MetadataPanel()

        # Create layout
        layout = QGridLayout()
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.toolbox)
        splitter.addWidget(self.table_view)
        splitter.addWidget(self.metadata_panel)
        splitter.setSizes([216, 432, 216])  # 1:4 ratio
        layout.addWidget(splitter, 0, 0)

        # Set grid as central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_actions(self):
        """Create the application's menu actions."""
        # Create actions for the File menu
        self.settings_act = QAction("Settings")
        self.settings_act.setShortcut("Ctrl+Alt+S")
        self.settings_act.setStatusTip("Edit application settings")
        self.settings_act.triggered.connect(self.open_settings)
        pixmap = QStyle.StandardPixmap.SP_BrowserReload
        reload_table_icon = self.style().standardIcon(pixmap)
        self.reload_table_act = QAction(reload_table_icon, "Reload")
        self.reload_table_act.setShortcut("F5")
        self.reload_table_act.setToolTip("Reload the active table")
        self.reload_table_act.triggered.connect(self.update_table)
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
        self.about_act.triggered.connect(self.about_dialogue)

    def toggle_full_screen(self, state) -> None:
        """Toggle full screen mode."""
        if state:
            self.showFullScreen()
        else:
            self.showNormal()

    def open_settings(self):
        """Open the settings window."""
        self.settings = SettingsWindow()

    def open_create_project(self):
        """
        Open the create project window; pass the database connection string so that
        the window can access the database.
        """
        self.create_project = CreateProjectWindow(self.connection_string)

    def create_window(self):
        """Create the application menu bar."""
        # Due to macOS guidelines, the menu bar will not appear in the GUI.
        self.menuBar().setNativeMenuBar(True)
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.settings_act)
        file_menu.addAction(self.reload_table_act)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_act)
        view_menu = self.menuBar().addMenu("View")
        appearance_submenu = view_menu.addMenu("Appearance")
        appearance_submenu.addAction(self.full_screen_act)
        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(self.about_act)

    def create_tool_bar(self) -> None:
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Add actions to the toolbar
        toolbar.addAction(self.about_act)
        toolbar.addAction(self.reload_table_act)

    def about_dialogue(self):
        """Display the About dialog."""
        QMessageBox.about(
            self,
            "About TAMS",
            """<h3>Tomography Archival and Management Software (TAMS)</h3>
            <h4>Version 0.1 (Development Build)</h4>
            <p>Original author: <a href='mailto:tom.kusonsuphanimit@manchester.ac.uk'>Tom Kusonsuphanimit</a> (The \
            University of Manchester).</p>
            <p>Copyright &copy; 2022 National X-ray Computed Tomography.</p>""",
        )

    def connect_to_database(self) -> None:
        """Set up the connection to the database."""
        config_file = Path("settings/database.toml").absolute()
        try:
            # Set up database
            logging.info("Connecting to database")
            config_dict = toml_operations.get_dict_from_toml(config_file)
            self.connection_string = dict_to_conn_str(config_dict)
            self.database_view = DatabaseView(self.connection_string)

            # Validate tables
            self.database_view.validate_tables()  # Raises exception if invalid.
            logging.info("All connection steps passed")
        except TypeError as exc:
            # Possibly raised on missing file due to attempted indexing of None
            logging.exception("Exception raised. Is config file missing?")
            QMessageBox.information(
                self,
                "Unable to connect; exception raised.",
                f"Check if config file is missing! Exception: {exc}",
                QMessageBox.StandardButton.Ok,
            )
        except ConnectionFailure as exc:
            logging.exception("Exception raised.")
            QMessageBox.warning(
                self,
                "Unable to connect to database",
                f"Exception: {exc}",
                QMessageBox.StandardButton.Ok,
            )
        except MissingTables as exc:
            logging.exception("Exception raised.")
            QMessageBox.warning(
                self,
                "Missing tables",
                f"Exception: {exc}",
                QMessageBox.StandardButton.Ok,
            )

    def current_table(self) -> str:
        """Get current table displayed."""
        _, current_table, _ = self.current_table_query
        return current_table

    def on_selection_changed(self):
        # Get row.
        proxy_index = self.table_view.currentIndex()
        source_index = self.proxy_model.mapToSource(proxy_index)
        row_index = source_index.row()
        print(row_index)
        row = self.table_model.get_row_data(row_index)
        key: int = row[0]
        if self.current_table() == "project":
            metadata = self.database_view.get_project_metadata(key)
        elif self.current_table() == "scan":
            metadata = self.database_view.get_scan_metadata(key)
        elif self.current_table() == '"user"':
            metadata = self.database_view.get_user_metadata(key)
        self.metadata_panel.update_metadata(metadata)
        self.metadata_panel.layout().update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec())
