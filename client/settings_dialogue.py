# -*- coding: utf-8 -*-
import logging
import sys
from pathlib import Path

import psycopg
from db import Database, dict_to_conn_str
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
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
    def __init__(self):
        super().__init__()
        self.initialize_ui()

    def initialize_ui(self):
        """Set up the settings window GUI."""
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Settings")
        self.database_toml_path = DATABASE_TOML_PATH.absolute()
        self.set_up_settings_window()
        self.show()

    def set_up_settings_window(self):
        """Create and arrange widgets in the settings window."""
        # Create tab bar and different page containers.
        tab_bar = QTabWidget(self)
        self.general_settings_tab = QWidget()
        self.database_settings_tab = QWidget()
        tab_bar.addTab(self.general_settings_tab, "General")
        tab_bar.addTab(self.database_settings_tab, "Database")

        # Call methods to create the pages.
        self.general_settings()
        self.database_settings()

        # Create buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        # When user clicks ok, apply settings and close box
        button_box.accepted.connect(self.accept)
        button_box.accepted.connect(self.apply)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self.apply
        )

        # Create the layout for the settings window.
        settings_v_box = QVBoxLayout()
        settings_v_box.addWidget(tab_bar)
        settings_v_box.addStretch()
        settings_v_box.addWidget(button_box)
        self.setLayout(settings_v_box)

    def general_settings(self):
        """General settings page allows the user to update software."""
        update_info_label = QLabel(
            """
        <h2>Updates</h2>
        <p>Keep this software up-to-date for the best performance, stability, and 
        security.</p>
        """
        )

        # Add widgets to general settings page layout
        tab_v_box = QVBoxLayout()
        tab_v_box.addWidget(update_info_label)
        tab_v_box.addStretch()

        # Set layout for general settings tab
        self.general_settings_tab.setLayout(tab_v_box)

    def database_settings(self):

        if not self.database_toml_path.is_file():
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
            toml_operations.create_toml(self.database_toml_path, template_db_config)
        database_config = toml_operations.get_dict_from_toml(self.database_toml_path)

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

    def apply(self):
        # Construct new config dict
        def update_if_modified(line_edit: QLineEdit, key: str):
            if line_edit.isModified():
                toml_operations.update_toml(
                    self.database_toml_path, "postgresql", key, line_edit.text()
                )

        update_if_modified(self.host_edit, "host")
        update_if_modified(self.port_edit, "port")
        update_if_modified(self.name_edit, "database")
        update_if_modified(self.user_edit, "user")
        update_if_modified(self.password_edit, "password")
        logging.info("Updated database.toml file.")

    def test_db_connection(self):
        try:
            if not self.database_toml_path.is_file():
                raise FileNotFoundError
            database_config_dict = toml_operations.get_dict_from_toml(
                self.database_toml_path
            )
            database_config = dict_to_conn_str(database_config_dict)
            with Database(database_config) as database:
                QMessageBox.information(
                    self,
                    "Connection success",
                    "Connected to database successfully.",
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

        except Exception as e:
            logging.exception("Exception raised")
            QMessageBox.critical(
                self,
                f"Unable to connect to database",
                str(e),
                QMessageBox.StandardButton.Cancel,
            )


if __name__ == "__main__":
    DATABASE_TOML_PATH = Path("settings/database.toml")
    app = QApplication(sys.argv)
    win = SettingsWindow()
    sys.exit(app.exec())
