"""Login dialogue to be used to connect to the database on the application startup.

Will allow user to save login credentials to a file for future use.
"""
from __future__ import annotations

import logging

from psycopg import errors
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

    def __init__(self: Login) -> None:
        """Initialize the login dialogue."""
        super().__init__(parent=None)

        # Set title
        self.setWindowTitle("Login")

        # Default settings for the database connection; assumes local database
        self.empty_settings: dict[str, dict[str, str]] = {
            "postgresql": {
                "host": "127.0.0.1",
                "port": "5432",
                "database": "",
                "user": "",
                "password": "",
                "remember": False,
            }
        }

        try:
            saved_settings = toml.load_toml(settings.database)
        except FileNotFoundError:
            logging.warning("No settings file found. Creating new settings file.")
            saved_settings = self.empty_settings
            toml.create_toml(settings.database, saved_settings)
        else:
            is_empty = tuple(
                not bool(value) for value in saved_settings["postgresql"].values()
            )
            if all(is_empty):
                msg = "Settings file is empty. Has the settings file been corrupted?"
                raise ValueError(msg)

        # Create the connection string from the saved settings
        # TODO: connect to the database automatically, if auto-login is enabled
        self.conn_str: str = utils.dict_to_conn_str(saved_settings)

        # Create layout
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
        pwd_edit: QLineEdit = self.form_layout.itemAt(7).widget()
        pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)

        # Add form to layout
        layout.addLayout(self.form_layout)

        # Create checkbox
        checkbox = QWidget()
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.checkbox = QCheckBox("Remember me")
        self.checkbox.setChecked(saved_settings["postgresql"]["remember"])
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

    def login(self: Login) -> None:
        """Attempt to log in using the input settings."""
        # Get the text from the line edit widgets in the form layout
        host_edit = self.form_layout.itemAt(1).widget()
        host = host_edit.text()
        port_edit = self.form_layout.itemAt(3).widget()
        port = port_edit.text()
        user_edit = self.form_layout.itemAt(5).widget()
        user = user_edit.text()
        pwd_edit = self.form_layout.itemAt(7).widget()
        pwd = pwd_edit.text()

        # Store the inputs in a dictionary
        data: dict[str, dict[str, str]] = {
            "postgresql": {
                "host": host,
                "port": port,
                "database": "tams",
                "user": user,
                "password": pwd,
                "remember": self.checkbox.isChecked(),
            }
        }

        # Create a connection string from the dictionary
        self.conn_str = utils.dict_to_conn_str(data)

        try:
            db = views.DatabaseView(self.conn_str)
            db.validate_tables()
            logging.info("Connected to database: %s", db)
        except errors.Error as exc:
            logging.exception("Failed to connect to database.")
            QMessageBox.critical(
                self,
                "Connection Error",
                (
                    "Failed to connect to database. Please check the login details.\n"
                    f"Exception raised: {exc}"
                ),
            )
            return

        if self.checkbox.isChecked():
            # If user has checked the checkbox, save the login information
            toml.create_toml(settings.database, data)
        else:
            # If user has not checked the checkbox, delete any saved login information
            toml.create_toml(settings.database, self.empty_settings)

        # Close the dialogue
        self.close()

    def cancel(self: Login) -> None:
        """Close the dialogue and exit the application."""
        self.close()
        raise SystemExit
