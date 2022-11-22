""" Create project dialogue window.

This window lets a user input and create a new project, which is added to the database
specified by the input connection string.
"""

import logging
from pathlib import Path

import psycopg
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from client import settings
from client.utils import file, toml


class CreatePrj(QDialog):
    """
    Window that takes project information and create and commits that project to the
    database specified by the connection string.
    """

    def __init__(self, conn_str: str):
        """Initialize the project creation dialogue."""

        super().__init__()
        self.conn_str: str = conn_str
        # Set up the settings window GUI.
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Create new project")
        self.set_up_settings_window()
        self.show()

    def set_up_settings_window(self) -> None:
        """Create and arrange widgets in the project creation window."""

        header_label = QLabel("Create new project")
        self.new_prj_title_entry = QLineEdit()
        self.new_prj_summary_entry = QLineEdit()
        self.new_prj_start_date_entry = QDateEdit(QDate().currentDate())
        self.new_prj_end_date_entry = QDateEdit(QDate().currentDate().addDays(1))

        # Arrange QLineEdit widgets in a QFormLayout
        dlg_form = QFormLayout()
        dlg_form.addRow("New project title:", self.new_prj_title_entry)
        dlg_form.addRow("New project summary:", self.new_prj_summary_entry)
        dlg_form.addRow("New project start date:", self.new_prj_start_date_entry)
        dlg_form.addRow("New project end date:", self.new_prj_end_date_entry)

        # Make create project button
        create_prj_button = QPushButton("Create new project")
        create_prj_button.clicked.connect(self.accept_prj_info)

        # Create the layout for the settings window.
        create_prj_v_box = QVBoxLayout()
        create_prj_v_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        create_prj_v_box.addWidget(header_label)
        create_prj_v_box.addSpacing(10)
        create_prj_v_box.addLayout(dlg_form, 1)
        create_prj_v_box.addWidget(create_prj_button)
        create_prj_v_box.addStretch()
        self.setLayout(create_prj_v_box)

    def accept_prj_info(self) -> None:
        """Read input data and save to database."""

        new_prj_title: str = self.new_prj_title_entry.text()
        new_prj_summary: str = self.new_prj_summary_entry.text()
        # The Qt toPython method specifies an object, not a date; however, it returns a date. Too bad.
        new_prj_start_date: object = self.new_prj_start_date_entry.date().toPython()
        new_prj_end_date: object = self.new_prj_end_date_entry.date().toPython()
        if new_prj_end_date < new_prj_start_date:
            QMessageBox.warning(
                self,
                "Date warning",
                "Project end date is before its start date. Please check inputs.",
                QMessageBox.StandardButton.Ok,
            )
            raise ValueError("Project end date is before its start date.")
        elif new_prj_title == "":
            QMessageBox.warning(
                self,
                "Title warning",
                "Project has no title. Please check inputs.",
                QMessageBox.StandardButton.Ok,
            )
            raise ValueError("Project title cannot be empty.")
        else:
            with psycopg.connect(self.conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "insert into project (title, summary, start_date, end_date) "
                        "values (%s, %s, %s, %s) returning project_id;",
                        (
                            new_prj_title,
                            new_prj_summary,
                            new_prj_start_date,
                            new_prj_end_date,
                        ),
                    )
                    conn.commit()
                    new_prj_id: int = cur.fetchone()[0]
                    # Check to see if project exists in local library
                    local_lib: Path = Path(
                        toml.get_value_from_toml(
                            settings.general, "storage", "local_library"
                        )
                    )
                    file.create_dir_if_missing(local_lib / str(new_prj_id))
                    logging.info("Created and committed project to database.")
                    QMessageBox.information(
                        self,
                        "Success",
                        "Project committed to database.",
                        QMessageBox.StandardButton.Ok,
                    )

            # Close window once done.
            self.close()
