"""
Login dialogue to be used to connect to the database on the application startup.

Will allow user to save login credentials to a file for future use.
"""
import logging
import sys

from psycopg import errors
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from client import settings
from client.db import utils, views
from client.utils import toml


class Login(QDialog):
    """Login dialogue."""

    def __init__(self):
        """Initialize the login dialogue."""

        super().__init__(parent=None)

        # Set title
        self.setWindowTitle("Login")

        # Load saved settings
        saved_settings = toml.load_toml(settings.database)

        # Set layout
        layout = QVBoxLayout()

        # Create form
        self.form_layout = QFormLayout()
        self.form_layout.addRow(
            "Host:", QLineEdit(saved_settings["postgresql"]["host"])
        )
        self.form_layout.addRow(
            "Port:", QLineEdit(saved_settings["postgresql"]["port"])
        )
        self.form_layout.addRow(
            "Username:", QLineEdit(saved_settings["postgresql"]["user"])
        )
        self.form_layout.addRow(
            "Password:", QLineEdit(saved_settings["postgresql"]["password"])
        )

        # The password line edit widget is the second child of the form layout (item 7)
        self.form_layout.itemAt(7).widget().setEchoMode(QLineEdit.EchoMode.Password)

        # Add form to layout
        layout.addLayout(self.form_layout)

        # Create checkbox
        checkbox = QWidget()
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.checkbox = QCheckBox("Remember me")
        checkbox_layout.addWidget(self.checkbox)
        checkbox.setLayout(checkbox_layout)

        # Add the checkbox to layout
        layout.addWidget(checkbox)

        # Create buttons
        buttons = QDialogButtonBox()
        buttons.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self.login)
        buttons.rejected.connect(self.cancel)

        # Add buttons to layout
        layout.addWidget(buttons)

        # Set layout
        self.setLayout(layout)

    def login(self):
        """Attempt to log in using the input settings."""

        # Get the text from the line edit widgets in the form layout
        host: str = self.form_layout.itemAt(1).widget().text()
        port: str = self.form_layout.itemAt(3).widget().text()
        user: str = self.form_layout.itemAt(5).widget().text()
        password: str = self.form_layout.itemAt(7).widget().text()

        # Store the inputs in a dictionary
        data: dict[str, dict[str, str]] = {
            "postgresql": {
                "host": host,
                "port": port,
                "database": "tams",
                "user": user,
                "password": password,
            }
        }

        # Create a connection string from the dictionary
        self.conn_str: str = utils.dict_to_conn_str(data)

        try:
            db = views.DatabaseView(self.conn_str)
            db.validate_tables()
            logging.info("Connected to database: %s", db)
        except errors.Error as exc:
            logging.exception("Failed to connect to database.")
            QMessageBox.critical(
                self,
                "Connection Error",
                "Failed to connect to database. Please the login details.\n"
                f"Exception raised: {exc}",
            )
            return

        # If the checkbox is checked, save the login information
        if self.checkbox.isChecked():
            toml.create_toml(settings.database, data)

        # Close the dialogue
        self.close()

    def cancel(self):
        """Close the dialogue and exit the application."""

        self.close()
        raise SystemExit

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec())