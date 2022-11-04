# -*- coding: utf-8 -*-
import logging
import sys
from pathlib import Path

import psycopg
from db import Database, dict_to_conn_str
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from settings import toml_operations

DATABASE_TOML_PATH = Path(r"settings/database.toml")


class SettingsWindow(QDialog):
    """Database settings dialogue allows to set the application settings."""
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Settings")
        self.general_settings_toml: Path = Path(r"settings/general.toml").absolute()
        self.database_toml: Path = DATABASE_TOML_PATH.absolute()
        self.set_up_settings_window()
        self.show()

    def set_up_settings_window(self) -> None:
        """Create and arrange widgets in the settings window."""

        # Create tab bar and different page containers.
        tab_bar: QTabWidget = QTabWidget(self)
        self.general_settings_tab: QWidget = QWidget()
        self.database_settings_tab: QWidget = QWidget()
        tab_bar.addTab(self.general_settings_tab, "General")
        tab_bar.addTab(self.database_settings_tab, "Database")

        # Call methods to create the pages.
        self.general_settings()
        self.database_settings()

        # Create buttons
        button_box: QDialogButtonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        # When user clicks OK, apply settings and close box
        button_box.accepted.connect(self.accept)
        button_box.accepted.connect(self.apply)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self.apply
        )

        # Create the layout for the settings window.
        settings_v_box: QVBoxLayout = QVBoxLayout()
        settings_v_box.addWidget(tab_bar)
        settings_v_box.addStretch()
        settings_v_box.addWidget(button_box)
        self.setLayout(settings_v_box)

    def general_settings(self) -> None:
        """General settings page allows to set the local library."""

        self.local_library_info = QLabel(
            self.generate_local_library_info()
        )
        self.local_library_info.setWordWrap(True)

        library_buttons: QWidget = QWidget()
        library_buttons_layout: QHBoxLayout = QHBoxLayout()

        open_library_button: QPushButton = QPushButton("Open local library")
        open_library_button.clicked.connect(self.open_local_library)
        library_buttons_layout.addWidget(open_library_button)

        edit_local_libary: QPushButton = QPushButton("Edit local library")
        edit_local_libary.clicked.connect(self.edit_local_library)
        library_buttons_layout.addWidget(edit_local_libary)

        library_buttons.setLayout(library_buttons_layout)

        # Add widgets to general settings page layout
        tab_v_box = QVBoxLayout()
        tab_v_box.addWidget(self.local_library_info)
        tab_v_box.addWidget(library_buttons)
        tab_v_box.addStretch()

        # Set layout for general settings tab
        self.general_settings_tab.setLayout(tab_v_box)

    def generate_local_library_info(self) -> str:
        """Generate the text to display the local library."""

        info: str = f"""
        <h2>Local library</h2>
        <p>
        Select the location of the local library. This directory will store scans for 
        syncing.
        </p>
        <p>
        <em>
        Current local library:<br>
            <samp><a href="{self.get_local_library()}">
                {self.get_local_library()}
            </a></samp>
        </em>
        </p>
        """
        return info

    def open_local_library(self) -> None:
        """Open the local library directory in the file explorer."""

        local_library = self.get_local_library()
        if local_library:
            QDesktopServices.openUrl(local_library)
    def get_local_library(self) -> str:
        """Get the current local library to present to the user."""

        current_local_library = toml_operations.get_value_from_toml(
            self.general_settings_toml, "storage", "local_library"
        )
        if current_local_library:
            return current_local_library
        return "No local library set."

    def database_settings(self):
        """Database settings widget to allow the user to set the database connection."""

        if not self.database_toml.is_file():
            # Create a database config file if one does not already exist
            template_db_config = {
                "postgresql": {
                    "host": "",
                    "port": "5432",
                    "database": "",
                    "user": "",
                    "password": "",
                }
            }
            toml_operations.create_toml(self.database_toml, template_db_config)
        database_config = toml_operations.get_dict_from_toml(self.database_toml)

        # Create database host widgets
        self.host_label = QLabel("Host")
        self.host_edit = QLineEdit(database_config["postgresql"]["host"])

        # Create database port widgets
        self.port_label = QLabel("Port")
        self.port_edit = QLineEdit(database_config["postgresql"]["port"])

        # Create database name widgets
        self.name_label = QLabel("Database name")
        self.name_edit = QLineEdit(database_config["postgresql"]["database"])

        # Create database user widgets
        self.user_label = QLabel("User")
        self.user_edit = QLineEdit(database_config["postgresql"]["user"])

        # Create database user widgets
        self.password_label = QLabel("Password")
        self.password_edit = QLineEdit(database_config["postgresql"]["password"])

        # Test connection, OK, cancel, and apply buttons
        self.test_button = QPushButton(self)
        self.test_button.setText("Test connection")
        self.test_button.setToolTip("Test the database connection")
        self.test_button.clicked.connect(self.test_db_connection)

        # Add widgets to general settings page layout
        tab_v_box = QVBoxLayout()
        tab_v_box.addWidget(self.host_label)
        tab_v_box.addWidget(self.host_edit)
        tab_v_box.addWidget(self.port_label)
        tab_v_box.addWidget(self.port_edit)
        tab_v_box.addWidget(self.name_label)
        tab_v_box.addWidget(self.name_edit)
        tab_v_box.addWidget(self.user_label)
        tab_v_box.addWidget(self.user_edit)
        tab_v_box.addWidget(self.password_label)
        tab_v_box.addWidget(self.password_edit)
        tab_v_box.addWidget(self.test_button)
        tab_v_box.addStretch()

        # Set layout for general settings tab
        self.database_settings_tab.setLayout(tab_v_box)

    def edit_local_library(self) -> None:
        """Open a file dialog to select the local library directory."""

        local_library = QFileDialog.getExistingDirectory(
            self, "Select local library directory"
        )
        if local_library:
            toml_operations.update_toml(
                self.general_settings_toml, "storage", "local_library", local_library
            )
        else:
            # If user cancels file dialog, do nothing
            pass

        # Update the local library info text
        self.local_library_info.setText(self.generate_local_library_info())

    def apply(self):
        """Apply the changes to settings."""
        # TODO: changes to the local library should be applied not immediately;
        #  refactor under this method!

        # Construct new config dict
        def update_if_modified(line_edit: QLineEdit, key: str):
            if line_edit.isModified():
                toml_operations.update_toml(
                    self.database_toml, "postgresql", key, line_edit.text()
                )

        update_if_modified(self.host_edit, "host")
        update_if_modified(self.port_edit, "port")
        update_if_modified(self.name_edit, "database")
        update_if_modified(self.user_edit, "user")
        update_if_modified(self.password_edit, "password")
        logging.info("Updated database.toml file.")

    def test_db_connection(self) -> None:
        """Test the database connection."""

        try:
            if not self.database_toml.is_file():
                raise FileNotFoundError
            database_config_dict = toml_operations.get_dict_from_toml(
                self.database_toml
            )
            database_config = dict_to_conn_str(database_config_dict)
            with Database(database_config) as database:
                QMessageBox.information(
                    self,
                    "Connection success",
                    "<p>Connected to database successfully.</p>"
                    f"<p>Version: <samp>{database}</samp></p>",
                    QMessageBox.StandardButton.Ok,
                )

        except psycopg.OperationalError as error:
            logging.exception(error)
            QMessageBox.critical(
                self,
                f"Database config incorrect",
                "Check database config settings are correct.",
                QMessageBox.StandardButton.Cancel,
            )

        except FileNotFoundError as error:
            logging.error(error)
            QMessageBox.critical(
                self,
                f"Database config file not found at {DATABASE_TOML_PATH}",
                "Check database config settings have been saved.",
                QMessageBox.StandardButton.Cancel,
            )

        except TypeError as error:
            logging.error(error)
            QMessageBox.critical(
                self,
                f"Database config file type error",
                "Check database config settings have been saved in the correct data type.",
                QMessageBox.StandardButton.Cancel,
            )

        except Exception as exc:
            logging.exception("Exception raised")
            QMessageBox.critical(
                self,
                "Unable to connect to database",
                str(exc),
                QMessageBox.StandardButton.Cancel,
            )


if __name__ == "__main__":
    DATABASE_TOML_PATH = Path("settings/database.toml")
    app = QApplication(sys.argv)
    win = SettingsWindow()
    sys.exit(app.exec())
