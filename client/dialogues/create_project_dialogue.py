""" Create project dialogue window.

This window lets a user input and create a new project, which is added to the database
specified by the input connection string.
"""

import logging

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


class CreateProjectWindow(QDialog):
    """
    Window that takes project information and create and commits that project to the
    database specified by the connection string.
    """

    def __init__(self, connection_string: str):
        super().__init__()
        self.connection_string: str = connection_string
        # Set up the settings window GUI.
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Create new project")
        self.set_up_settings_window()
        self.show()

    def set_up_settings_window(self) -> None:
        """Create and arrange widgets in the project creation window."""

        header_label = QLabel("Create new project")
        self.new_project_title_entry = QLineEdit()
        self.new_project_summary_entry = QLineEdit()
        self.new_project_start_date_entry = QDateEdit(QDate().currentDate())
        self.new_project_end_date_entry = QDateEdit(QDate().currentDate().addDays(1))

        # Arrange QLineEdit widgets in a QFormLayout
        dialogue_form = QFormLayout()
        dialogue_form.addRow("New project title:", self.new_project_title_entry)
        dialogue_form.addRow("New project summary:", self.new_project_summary_entry)
        dialogue_form.addRow(
            "New project start date:", self.new_project_start_date_entry
        )
        dialogue_form.addRow("New project end date:", self.new_project_end_date_entry)

        # Make create project button
        create_project_button = QPushButton("Create new project")
        create_project_button.clicked.connect(self.accept_project_info)

        # Create the layout for the settings window.
        create_project_v_box = QVBoxLayout()
        create_project_v_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        create_project_v_box.addWidget(header_label)
        create_project_v_box.addSpacing(10)
        create_project_v_box.addLayout(dialogue_form, 1)
        create_project_v_box.addWidget(create_project_button)
        create_project_v_box.addStretch()
        self.setLayout(create_project_v_box)

    def accept_project_info(self) -> None:
        """Read input data and save to database."""

        new_project_title: str = self.new_project_title_entry.text()
        new_project_summary: str = self.new_project_summary_entry.text()
        # The Qt toPython method specifies an object, not a date; however, it returns a date. Too bad.
        new_project_start_date: object = (
            self.new_project_start_date_entry.date().toPython()
        )
        new_project_end_date: object = self.new_project_end_date_entry.date().toPython()
        if new_project_end_date < new_project_start_date:
            logging.warning(
                "Tried to create a project with an end date before the start date."
            )
            QMessageBox.warning(
                self,
                "Date warning",
                "Project end date is before its start date. Please check inputs.",
                QMessageBox.StandardButton.Ok,
            )
        elif new_project_title == "":
            logging.warning("Tried to create a project without a title.")
            QMessageBox.warning(
                self,
                "Title warning",
                "Project has no title. Please check inputs.",
                QMessageBox.StandardButton.Ok,
            )
        else:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "insert into project (title, summary, start_date, end_date) "
                        "values (%s, %s, %s, %s);",
                        (
                            new_project_title,
                            new_project_summary,
                            new_project_start_date,
                            new_project_end_date,
                        ),
                    )
                    conn.commit()
                    logging.info("Created and committed project to database.")
                    QMessageBox.information(
                        self,
                        "Success",
                        "Project committed to database.",
                        QMessageBox.StandardButton.Ok,
                    )

            # Close window once done.
            self.close()
