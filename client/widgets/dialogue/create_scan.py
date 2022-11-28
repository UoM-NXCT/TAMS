"""
This window lets a user input and create a new scan, which is added to the database
specified by the input connection string.
"""

import logging
from pathlib import Path
from typing import Any

import psycopg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from client import settings
from client.db.views import DatabaseView
from client.utils import file, toml


class CreateScan(QDialog):
    """
    Window that takes project information and create and commits that project to the
    database specified by the connection string.
    """

    def __init__(self, conn_str: str) -> None:
        super().__init__()
        self.conn_str: str = conn_str

        # Set up the settings window GUI.
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Create new scan")
        self.set_up_scan_dlg()
        self.show()

    def set_up_scan_dlg(self) -> None:
        """Create and arrange widgets in the project creation window."""

        header_label: QLabel = QLabel("Create new scan")

        # Get project ID options
        self.new_scan_prj_id_entry = QComboBox()
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("select project_id, title from project;")
                raw_prj_ids: list[tuple[Any, ...]] = cur.fetchall()
                # Hack the output into a value QComboBox likes (a list of strings)
                prj_ids: list[str] = [
                    f"{tuple_value[0]} ({tuple_value[1]})"
                    for tuple_value in raw_prj_ids
                ]
        self.new_scan_prj_id_entry.addItems(prj_ids)

        # Get instrument ID options
        self.new_scan_instrument_id_entry = QComboBox()
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("select instrument_id, name from instrument;")
                raw_instrument_ids: list[tuple[Any, ...]] = cur.fetchall()
                # Hack the output into a value the Qt ComboBox likes (a list of strings)
                instrument_ids: list[str] = [
                    f"{tuple_value[0]} ({tuple_value[1]})"
                    for tuple_value in raw_instrument_ids
                ]
        self.new_scan_instrument_id_entry.addItems(instrument_ids)

        # Arrange QLineEdit widgets in a QFormLayout
        dlg_form = QFormLayout()
        dlg_form.addRow("New scan project id:", self.new_scan_prj_id_entry)
        dlg_form.addRow("New scan instrument id:", self.new_scan_instrument_id_entry)

        # Make create project button
        create_scan_button = QPushButton("Create new scan")
        create_scan_button.clicked.connect(self.accept_new_scan_info)

        # Create the layout for the settings window.
        create_prj_v_box = QVBoxLayout()
        create_prj_v_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        create_prj_v_box.addWidget(header_label)
        create_prj_v_box.addSpacing(10)
        create_prj_v_box.addLayout(dlg_form, 1)
        create_prj_v_box.addWidget(create_scan_button)
        create_prj_v_box.addStretch()
        self.setLayout(create_prj_v_box)

    def get_scan_form_data(self, scan_id: int) -> dict[str, dict[str, Any]]:
        """Get scan form data for user_form.toml."""

        # Get immutable data (data that should not be changed by the user)
        db_view: DatabaseView = DatabaseView(self.conn_str)
        immutable_data, immutable_column_headers = db_view.view_select_from_where(
            "scan_id, project_id, instrument_id",
            "scan",
            f"scan_id={scan_id}",
        )
        data: dict[str, dict[str, Any]] = {
            "hardcoded": dict(zip(immutable_column_headers, immutable_data[0])),
        }
        return data

    def accept_new_scan_info(self) -> None:
        """Read input data and save to database."""

        # Get IDs from the combo boxes
        selected_project_id: int = int(
            self.new_scan_prj_id_entry.currentText().split()[0]
        )
        selected_instrument_id: int = int(
            self.new_scan_instrument_id_entry.currentText().split()[0]
        )

        db_view: DatabaseView = DatabaseView(self.conn_str)
        prj_exists: bool = db_view.prj_exists(selected_project_id)
        instrument_exists: bool = db_view.instrument_exists(selected_instrument_id)

        if not prj_exists:
            logging.warning(
                "Tried to create a scan with a project id that does not exist."
            )
            QMessageBox.warning(
                self,
                "Invalid project id",
                "Project id does not exist. Please check inputs.",
                QMessageBox.StandardButton.Ok,
            )
            return
        if not instrument_exists:
            logging.warning(
                "Tried to create a scan with an instrument ID that does not exist."
            )
            QMessageBox.warning(
                self,
                "Invalid instrument ID",
                "Instrument ID does not exist. Please check inputs.",
                QMessageBox.StandardButton.Ok,
            )
            return

        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"insert into scan (project_id, instrument_id) values ({selected_project_id}, {selected_instrument_id}) returning scan_id;"
                )
                conn.commit()
                scan_id: int = cur.fetchone()[
                    0
                ]  # May raise TypeError if no scan_id rows returned
                # Check to see if the newly created scan exists in the local library and create it if not
                local_lib: Path = Path(settings.get_lib("local"))
                scan_dir: Path = local_lib / str(selected_project_id) / str(scan_id)
                file.create_dir(scan_dir)
                file.create_dir(scan_dir / "tams_meta")
                form: Path = scan_dir / "tams_meta" / "user_form.toml"
                immutable_fields: dict[str, Any] = self.get_scan_form_data(scan_id)
                mutable_fields: dict[str, Any] = {
                    "mutable": {
                        "example": "",
                    }
                }
                scan_form_data: dict[str, Any] = immutable_fields | mutable_fields
                toml.create_toml(form, scan_form_data)
                # Create README.txt
                readme: Path = scan_dir / "tams_meta" / "README.txt"
                with open(readme, "w") as f:
                    f.write("Placeholder file for README.txt")
                perm_dir_name = settings.get_perm_dir_name()
                file.create_dir(
                    local_lib / str(selected_project_id) / str(scan_id) / perm_dir_name
                )
                logging.info("Created and committed scan to database.")
                QMessageBox.information(
                    self,
                    "Success",
                    "Scan committed to database.",
                    QMessageBox.StandardButton.Ok,
                )
            # Close window once done.
            self.close()
