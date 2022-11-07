"""
This window lets a user input and create a new scan, which is added to the database
specified by the input connection string.
"""

import logging

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


class CreateScanDialogue(QDialog):
    """
    Window that takes project information and create and commits that project to the
    database specified by the connection string.
    """

    def __init__(self, connection_string: str) -> None:
        super().__init__()
        self.connection_string: str = connection_string

        # Set up the settings window GUI.
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Create new scan")
        self.set_up_scan_dialogue()
        self.show()

    def set_up_scan_dialogue(self) -> None:
        """Create and arrange widgets in the project creation window."""

        header_label: QLabel = QLabel("Create new scan")

        # Get project ID options
        self.new_scan_project_id_entry = QComboBox()
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute("select project_id, title from project;")
                raw_project_ids: list[tuple[int, str]] = cur.fetchall()
                # Hack the output into a value the Qt ComboBox likes (a list of strings)
                project_ids: list[str] = [
                    f"{tuple_value[0]} ({tuple_value[1]})"
                    for tuple_value in raw_project_ids
                ]
        self.new_scan_project_id_entry.addItems(project_ids)

        # Get instrument ID options
        self.new_scan_instrument_id_entry = QComboBox()
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute("select instrument_id, name from instrument;")
                raw_instrument_ids: list[tuple[int, str]] = cur.fetchall()
                # Hack the output into a value the Qt ComboBox likes (a list of strings)
                instrument_ids: list[str] = [
                    f"{tuple_value[0]} ({tuple_value[1]})"
                    for tuple_value in raw_instrument_ids
                ]
        self.new_scan_instrument_id_entry.addItems(instrument_ids)

        # Arrange QLineEdit widgets in a QFormLayout
        dialogue_form = QFormLayout()
        dialogue_form.addRow("New scan project id:", self.new_scan_project_id_entry)
        dialogue_form.addRow(
            "New scan instrument id:", self.new_scan_instrument_id_entry
        )

        # Make create project button
        create_scan_button = QPushButton("Create new scan")
        create_scan_button.clicked.connect(self.accept_new_scan_info)

        # Create the layout for the settings window.
        create_project_v_box = QVBoxLayout()
        create_project_v_box.setAlignment(Qt.AlignTop)
        create_project_v_box.addWidget(header_label)
        create_project_v_box.addSpacing(10)
        create_project_v_box.addLayout(dialogue_form, 1)
        create_project_v_box.addWidget(create_scan_button)
        create_project_v_box.addStretch()
        self.setLayout(create_project_v_box)

    def accept_new_scan_info(self) -> None:
        """Read input data and save to database."""

        def project_id_exists(project_id: int) -> bool:
            """Check if a project with a given project id exists in the database."""

            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"select project_id from project where project_id={project_id}"
                    )
                    rows: list = cur.fetchall()

            # Returns false if the list is empty (no rows returned)
            if len(rows) > 1:
                logging.warning(
                    "Multiple projects with the same project id; this shouldn't happen!"
                )

            return bool(rows)

        def instrument_id_exists(instrument_id: int) -> bool:
            """Check if a project with a given instrument ID exists in the database."""

            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"select instrument_id from instrument where instrument_id={instrument_id}"
                    )
                    rows: list = cur.fetchall()

            # Returns false if the list is empty (no rows returned)
            if len(rows) > 1:
                logging.warning(
                    "Multiple instrument with the same instrument id; this shouldn't happen!"
                )

            return bool(rows)

        # Get IDs from the combo boxes
        selected_project_id: int = int(
            self.new_scan_project_id_entry.currentText().split()[0]
        )
        selected_instrument_id: int = int(
            self.new_scan_instrument_id_entry.currentText().split()[0]
        )

        if not project_id_exists(selected_project_id):
            logging.warning(
                "Tried to create a scan with a project id that does not exist."
            )
            QMessageBox.warning(
                self,
                "Invalid project id",
                "Project id does not exist. Please check inputs.",
                QMessageBox.StandardButton.Ok,
            )
        elif not instrument_id_exists(selected_instrument_id):
            logging.warning(
                "Tried to create a scan with an instrument ID that does not exist."
            )
            QMessageBox.warning(
                self,
                "Invalid instrument ID",
                "Instrument ID does not exist. Please check inputs.",
                QMessageBox.StandardButton.Ok,
            )
        else:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"insert into scan (project_id, instrument_id) values ({selected_project_id}, {selected_instrument_id});"
                    )
                    conn.commit()
                    logging.info("Created and committed scan to database.")
                    QMessageBox.information(
                        self,
                        "Success",
                        "Scan committed to database.",
                        QMessageBox.StandardButton.Ok,
                    )
            # Close window once done.
            self.close()
