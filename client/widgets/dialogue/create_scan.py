"""
This window lets a user input and create a new scan, which is added to the database
specified by the input connection string.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import psycopg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCompleter,
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from client import settings
from client.db.views import DatabaseView
from client.utils import file, log, toml

from .decorators import handle_common_exc

if TYPE_CHECKING:
    from typing import Any

    from PySide6.QtWidgets import QWidget


class CreateScan(QDialog):
    """
    Window that takes project information and create and commits that project to the
    database specified by the connection string.
    """

    def __init__(self, parent_widget: QWidget, conn_str: str) -> None:
        super().__init__(parent=parent_widget)
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
        self.new_scan_prj_id_entry: QLineEdit = QLineEdit()
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("select project_id, title from project;")
                raw_prj_ids: list[tuple[Any, ...]] = cur.fetchall()
                # Hack the output into a value QComboBox likes (a list of strings)
                prj_ids: list[str] = [
                    f"{tuple_value[0]} ({tuple_value[1]})"
                    for tuple_value in raw_prj_ids
                ]
        completer = QCompleter(prj_ids)
        completer.setFilterMode(Qt.MatchContains)
        self.new_scan_prj_id_entry.setCompleter(completer)

        # Get instrument ID options
        self.new_scan_instrument_id_entry = QLineEdit()
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("select instrument_id, name from instrument;")
                raw_instrument_ids: list[tuple[Any, ...]] = cur.fetchall()
                # Hack the output into a value the Qt ComboBox likes (a list of strings)
                instrument_ids: list[str] = [
                    f"{tuple_value[0]} ({tuple_value[1]})"
                    for tuple_value in raw_instrument_ids
                ]
        completer = QCompleter(instrument_ids)
        completer.setFilterMode(Qt.MatchContains)
        self.new_scan_instrument_id_entry.setCompleter(completer)

        # Arrange QLineEdit widgets in a QFormLayout
        dlg_form: QFormLayout = QFormLayout()
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

    @handle_common_exc
    def accept_new_scan_info(self) -> None:
        """Read input data and save to database."""

        # Get IDs from the combo boxes
        selected_prj_id: int = int(self.new_scan_prj_id_entry.text().split()[0])
        selected_instrument_id: int = int(
            self.new_scan_instrument_id_entry.text().split()[0]
        )

        db_view: DatabaseView = DatabaseView(self.conn_str)

        # Check the project and instrument IDs are valid
        if not db_view.prj_exists(selected_prj_id):
            raise RuntimeError(
                "Tried to create a scan with a project ID that does not exist."
            )
        if not db_view.instrument_exists(selected_instrument_id):
            raise RuntimeError(
                "Tried to create a scan with an instrument ID that does not exist."
            )

        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    (
                        "insert into scan (project_id, instrument_id) values (%s, %s)"
                        " returning scan_id;"
                    ),
                    (selected_prj_id, selected_instrument_id),
                )
                conn.commit()
                scan_id: int = cur.fetchone()[
                    0
                ]  # May raise TypeError if no scan_id rows returned
                # Check if new scan exists in the local library and create it if not
                local_lib: Path = Path(settings.get_lib("local"))
                scan_dir: Path = local_lib / str(selected_prj_id) / str(scan_id)
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
                with open(
                    scan_dir / "tams_meta" / "README.txt", "w", encoding="utf-8"
                ) as f:
                    f.write("Placeholder file for README.txt")
                perm_dir_name = settings.get_perm_dir_name()
                file.create_dir(
                    local_lib / str(selected_prj_id) / str(scan_id) / perm_dir_name
                )

                # Inform the user that the scan was created and committed
                log.logger(__name__).info("Created and committed scan to database.")
                QMessageBox.information(
                    self,
                    "Success",
                    "Scan committed to database.",
                    QMessageBox.StandardButton.Ok,
                )

            # Close window once done.
            self.close()
