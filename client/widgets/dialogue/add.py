"""
This window lets users add scans to the library.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from client.library import NikonScan, get_relative_path, local_path
from client.runners.add_scan import AddScan
from client.utils.file import create_dir
from client.utils.toml import load_toml


class AddToLibraryProgress(QDialog):
    """Progress window for adding scans to the library."""

    def __init__(self, runner: AddScan, parent_dlg: QDialog) -> None:
        """Initialize the window."""

        super().__init__(parent=parent_dlg)

        self.setWindowTitle("Adding data to library")
        layout: QVBoxLayout = QVBoxLayout()
        label: QLabel = QLabel("Adding data to library...")
        layout.addWidget(label)
        # TODO: Add progress bar
        # TODO: Add stop, pause, resume buttons
        # NOTE: Both tasks above should be very similar to what was done for the
        #  download functionality; it should be possible to copy and paste.
        self.setLayout(layout)

        self.threadpool: QThreadPool = QThreadPool()
        self.runner: AddScan = runner
        self.threadpool.start(self.runner)

        self.show()


class AddToLibrary(QDialog):
    """Window for adding scans to the library."""

    def _set_up_settings_window(self) -> None:
        """Create and arrange widgets in the project creation window."""

        header_label = QLabel("Add new scan to library")

        # Get scan format
        scan_fmt_label = QLabel("Select scan format:")
        self.scan_fmt = QComboBox()
        self.scan_fmt.addItems(("Nikon",))

        # Get scan location
        self.scan_loc_label = QLabel("Select scan location:")
        self.scan_loc_btn = QPushButton("Edit scan location")
        self.scan_loc_btn.clicked.connect(self.select_scan_loc)

        # Create project ID and scan ID fields
        self.id_form = QFormLayout()
        self.prj_id_line_edit = QLineEdit(str(self.prj_id))
        self.id_form.addRow("Project ID:", self.prj_id_line_edit)
        self.scan_id_line_edit = QLineEdit(str(self.scan_id))
        self.id_form.addRow("Scan ID:", self.scan_id_line_edit)
        self.instrument_id_line_edit = QLineEdit(str(self.instrument_id))
        self.id_form.addRow("Instrument ID:", self.instrument_id_line_edit)

        # Create the tree widget
        self.metadata_tree: QTreeWidget = QTreeWidget()
        self.metadata_tree.setColumnCount(1)
        # Hide the header; our tree is vertical so there is no reason to include it.
        self.metadata_tree.setHeaderHidden(True)

        # Create checkbox
        self.add_to_db_checkbox = QCheckBox("Add to database")

        # Make create project button
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_scan)

        # Create the layout for the settings window.
        v_box = QVBoxLayout()
        v_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        v_box.addWidget(header_label)
        v_box.addWidget(scan_fmt_label)
        v_box.addWidget(self.scan_fmt)
        v_box.addWidget(self.scan_loc_label)
        v_box.addWidget(self.scan_loc_btn)
        v_box.addLayout(self.id_form)
        v_box.addWidget(self.metadata_tree)
        v_box.addWidget(self.add_to_db_checkbox)
        v_box.addWidget(add_btn)
        v_box.addStretch()
        self.setLayout(v_box)

    def __init__(
        self, conn_str: str, scan_id: int | None, prj_id: int | None, *args, **kwargs
    ) -> None:
        """Initialize the window."""

        super().__init__(*args, **kwargs)
        self.conn_str: str = conn_str
        self.scan_id: int = scan_id
        self.prj_id: int = prj_id
        self.instrument_id: int | None = None
        self.scan_loc: Path | None = None

        # Set up the settings window GUI.
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Add to library")
        self._set_up_settings_window()
        self.show()

    def update_metadata_tree(self) -> None:
        """Update the metadata tree with the new scan metadata."""
        self.metadata_tree.clear()
        fmt: str = self.scan_fmt.currentText()
        match fmt:
            case "Nikon":
                scan = NikonScan(self.scan_loc)
                try:
                    metadata = scan.get_metadata()
                    items: list[QTreeWidgetItem] = []
                    for index, (key, value) in enumerate(metadata.items()):
                        item = QTreeWidgetItem([key])
                        child = QTreeWidgetItem([str(value)])
                        item.addChild(child)
                        items.append(item)
                    self.metadata_tree.insertTopLevelItems(0, items)
                    self.metadata_tree.expandAll()
                except FileNotFoundError:
                    QMessageBox.warning(
                        self,
                        "Metadata not found",
                        (
                            "Could not find scan metadata. Please check the correct"
                            " scan format has been selected and that the scan directory"
                            " is valid."
                        ),
                    )

            case _:
                raise NotImplementedError(f"Scan format {fmt} not implemented.")

    def read_user_form(self) -> None:
        """Read the user's input from the form."""

        if not self.scan_loc:
            raise ValueError("Scan location not set.")
        toml_path = self.scan_loc / "user_form.toml"
        if toml_path.exists():
            metadata = load_toml(toml_path)
            try:
                self.prj_id = metadata["scan"]["project_id"]
                self.prj_id_line_edit.setText(str(self.prj_id))
            except KeyError:
                # If the project ID is not in the TOML file, do nothing.
                pass
            try:
                self.scan_id = metadata["scan"]["scan_id"]
                self.scan_id_line_edit.setText(str(self.scan_id))
            except KeyError:
                # If the scan ID is not in the TOML file, do nothing.
                pass
            try:
                self.instrument_id = metadata["scan"]["instrument_id"]
                self.instrument_id_line_edit.setText(str(self.instrument_id))
            except KeyError:
                # If the instrument ID is not in the TOML file, do nothing.
                pass

    def select_scan_loc(self) -> None:
        """Select the scan location."""
        if self.scan_loc:
            init_dir: Path = self.scan_loc
        else:
            init_dir = Path.home()
        self.scan_loc = Path(
            QFileDialog.getExistingDirectory(
                self,
                caption="Select scan directory",
                dir=str(init_dir),
                options=QFileDialog.Option.ShowDirsOnly,
            )
        )
        if self.scan_loc:
            self.scan_loc_label.setText(f"Scan location: {self.scan_loc}")
        else:
            self.scan_loc_label.setText("Select scan location:")
            QMessageBox.warning(
                self,
                "No directory set",
                "No directory set. Please set a directory first.",
            )
        self.update_metadata_tree()
        self.read_user_form()

    def add_to_database(self, fmt: str) -> None:
        """Add the scan to the database.

        At present, we save: scan ID, project ID, instrument ID, scan name, voltage, and amperage.
        """
        if not self.scan_id or not self.prj_id:
            raise ValueError("Scan ID or project ID not set.")
        scan_metadata: dict[str, Any] = {}
        match fmt:
            case "Nikon":
                scan = NikonScan(self.scan_loc)
                scan_metadata = scan.get_metadata()

        # Update scan metadata with user input.
        with psycopg.connect(self.conn_str) as conn:
            # Create project and scan if it does not exist already.
            with conn.cursor() as cur:
                cur.execute(
                    (
                        "insert into project (project_id) values (%s) on conflict on"
                        " constraint project_pk do nothing;"
                    ),
                    (self.prj_id,),
                )
                cur.execute(
                    (
                        "insert into scan (scan_id, project_id, instrument_id) values"
                        " (%s, %s, %s) on conflict on constraint scan_pk do nothing;"
                    ),
                    (self.scan_id, self.prj_id, self.instrument_id),
                )
                # Update scan metadata.
                for col, value in scan_metadata.items():
                    # Perform pyscopg gymnastics for safe(r) SQL queries.
                    # See https://www.psycopg.org/psycopg3/docs/api/sql.html
                    cur.execute(
                        sql.SQL("update scan set {col} = %s where scan_id = %s").format(
                            col=sql.Identifier(col)
                        ),
                        (value, self.scan_id),
                    )

    def add_scan(self) -> None:
        """Add the scan to the library."""

        # If the user selected add to database, warn them about the consequences.
        if self.add_to_db_checkbox.isChecked():
            reply = QMessageBox.question(
                self,
                "Add to database?",
                (
                    "Are you sure you want to add this data to the database? If scans"
                    " or projects that already exist in the database are added, their"
                    " metadata will be overwritten by the loaded metadata."
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # For a scan to be saved, we need its project ID and scan ID as a minimum.

        # Create directories in local library if they don't exist
        relative_path: Path = get_relative_path(self.prj_id, self.scan_id)
        local_dir: Path = local_path(relative_path)
        create_dir(local_dir)

        fmt: str = self.scan_fmt.currentText()
        match fmt:
            case "Nikon":
                # Add to database
                if self.add_to_db_checkbox.isChecked():
                    self.add_to_database(fmt)
                # Copy the scan to the local library
                scan = NikonScan(self.scan_loc)
                runner = AddScan(self.prj_id, self.scan_id, scan)
                AddToLibraryProgress(runner, self)
            case _:
                raise NotImplementedError(f"Scan format {fmt} not implemented.")
