"""Main window for the GUI."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from client import actions
from client.db import DatabaseView
from client.utils import log
from client.widgets.dialogue import CreatePrj, CreateScan, Login
from client.widgets.metadata_panel import MetadataPanel
from client.widgets.table import TableView
from client.widgets.toolbox import ToolBox

if TYPE_CHECKING:
    from client.widgets.dialogue import DownloadScans

TAMS_ROOT = Path(__file__).parents[1]

logger = log.logger(__name__)


class MainWindow(QMainWindow):
    """The main Qt window for the database application."""

    def _create_actions(self: MainWindow) -> None:
        """Create the application actions.

        Must be called only during initialization (__init__).
        """
        # Create actions for the File menu
        self.settings_act = actions.OpenSettings(self)
        self.update_table_act = actions.UpdateTable(self)
        self.download_act = actions.DownloadData(self)
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

    def _set_up_main_window(self: MainWindow) -> None:
        """Create and arrange widgets in the main window.

        This method should only be called during initialization (__init__).
        """
        # Create status bar
        self.setStatusBar(QStatusBar())

        # Create metadata panel
        self.metadata_panel = MetadataPanel()

        # Create table
        table_widget = QWidget()
        self.table_layout = QVBoxLayout()
        self.table_view = TableView()
        self.table_view.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.table_view.doubleClicked.connect(self.open_act.trigger)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search the table...")
        self.table_layout.addWidget(self.search)
        self.table_layout.addWidget(self.table_view)
        table_widget.setLayout(self.table_layout)

        # Create toolbox
        # TODO: Refactor to make this consistent with how we handle actions elsewhere!
        self.toolbox.prj_btn.clicked.connect(self.update_table_act.with_projects)
        self.toolbox.create_prj_btn.clicked.connect(
            lambda: CreatePrj(self, self.conn_str)
        )
        self.toolbox.scans_btn.clicked.connect(self.update_table_act.with_scans)
        self.toolbox.create_scan_btn.clicked.connect(
            lambda: CreateScan(self, self.conn_str)
        )
        self.toolbox.users_btn.clicked.connect(self.update_table_act.with_users)

        # Create layout
        layout = QGridLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.toolbox)
        splitter.addWidget(table_widget)
        splitter.addWidget(self.metadata_panel)
        splitter.setSizes([216, 432, 216])  # 1:4 ratio
        layout.addWidget(splitter, 0, 0)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _create_tool_bar(self: MainWindow) -> None:
        """Create the application toolbar.

        This method should only be called during initialization (__init__).
        """
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        toolbar.addAction(self.update_table_act)
        toolbar.addAction(self.add_act)
        toolbar.addAction(self.download_act)
        toolbar.addAction(self.upload_act)
        toolbar.addAction(self.open_act)
        toolbar.addAction(self.validate_act)
        toolbar.addSeparator()
        toolbar.addAction(self.about_act)

    def _create_window(self: MainWindow) -> None:
        """Create the application menu bar.

        This method should only be called during initialization (__init__).
        """
        # Due to macOS guidelines, the menu bar will not appear in the GUI
        self.menuBar().setNativeMenuBar(True)
        # Create the File menu
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.settings_act)
        file_menu.addAction(self.update_table_act)
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

    def __init__(self: MainWindow) -> None:
        """Initialize the main window."""
        super().__init__()

        # Create empty variables for use later.
        self.db_view = None
        self.conn_str = ""
        self.table_model = None
        self.proxy_model = None
        self.current_table_query = (
            None,
            None,
            None,
        )  # (cols, table, filter)
        self.toolbox = ToolBox()
        self.current_metadata = None

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

        self._create_actions()
        self._set_up_main_window()
        self._create_window()
        self._create_tool_bar()
        self.update_table_act.with_projects()
        self.show()

        self.update_table_act.trigger()

    def get_value_from_row(self: MainWindow, column: int) -> Any:  # noqa: ANN401
        """Get the value of a column in the selected row in the table view."""
        row = self.selected_row()
        return row[column]

    def current_table(self: MainWindow) -> str | None:
        """Get the current table displayed."""
        return self.current_table_query[1]

    def selected_row(self: MainWindow) -> tuple[Any, ...]:
        """Get the selected row in the table view."""
        try:
            # Rows can be sorted, so the Nth table item may not be the Nth data item.
            # Hence, we have to translate the visible index to the source index!
            # TODO: Find a way to handle PySide6 behaviour without mypy complaining.
            proxy_index = self.table_view.currentIndex()
            src_index = self.proxy_model.mapToSource(  # type: ignore[attr-defined]
                proxy_index
            )
            row_index = src_index.row()
            row = self.table_model.get_row_data(row_index)  # type: ignore[attr-defined]
        except AttributeError as exc:
            msg = "No row selected. Please select a row and try again."
            raise ValueError(msg) from exc
        else:
            if isinstance(row, tuple):
                return row
            # This shouldn't happen, but it is theoretically possible.
            msg = "Non-tuple returned without raising AttributeError. Please report!"
            raise RuntimeError(msg)
