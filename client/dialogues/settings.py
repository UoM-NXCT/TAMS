"""
Settings dialogue for the user to view and change settings.

Settings are saved as TOML files in the settings directory.
"""

import logging
import sys
from pathlib import Path

import psycopg
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
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

from client import settings
from client.db import Database, dict_to_conn_str
from client.utils.toml import (
    create_toml,
    get_dict_from_toml,
    get_value_from_toml,
    update_toml,
)


class SettingsWindow(QDialog):
    """Database settings dialogue allows to set the application settings."""

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Settings")

        # Store paths to settings TOML files
        settings_dir: Path = Path(__file__).parents[1] / "settings"

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
        """General settings page allows to set the local and permanent library."""

        # Create the layout for the local library settings.
        self.local_library_info = QLabel(self.generate_local_library_info())
        self.local_library_info.setWordWrap(True)

        local_lib_buttons: QWidget = QWidget()
        local_lib_buttons_layout: QHBoxLayout = QHBoxLayout()

        open_local_lib_button: QPushButton = QPushButton("Open local library")
        open_local_lib_button.clicked.connect(
            lambda: self.open_library(self.get_library("local"), "local")
        )
        local_lib_buttons_layout.addWidget(open_local_lib_button)

        edit_local_libary: QPushButton = QPushButton("Edit local library")
        edit_local_libary.clicked.connect(lambda: self.edit_library("local"))
        local_lib_buttons_layout.addWidget(edit_local_libary)

        local_lib_buttons.setLayout(local_lib_buttons_layout)

        # Create the layout for the permanent library settings.
        self.permanent_library_info = QLabel(self.generate_permanent_library_info())
        self.permanent_library_info.setWordWrap(True)

        permanent_lib_buttons: QWidget = QWidget()
        permanent_lib_buttons_layout: QHBoxLayout = QHBoxLayout()

        open_permanent_lib_button: QPushButton = QPushButton("Open permanent library")
        open_permanent_lib_button.clicked.connect(
            lambda: self.open_library(self.get_library("permanent"), "permanent")
        )
        permanent_lib_buttons_layout.addWidget(open_permanent_lib_button)

        edit_permanent_lib: QPushButton = QPushButton("Edit permanent library")
        edit_permanent_lib.clicked.connect(lambda: self.edit_library("permanent"))
        permanent_lib_buttons_layout.addWidget(edit_permanent_lib)

        permanent_lib_buttons.setLayout(permanent_lib_buttons_layout)

        # Add widgets to general settings page layout
        tab_v_box = QVBoxLayout()
        tab_v_box.addWidget(self.local_library_info)
        tab_v_box.addWidget(local_lib_buttons)
        tab_v_box.addWidget(self.permanent_library_info)
        tab_v_box.addWidget(permanent_lib_buttons)
        tab_v_box.addStretch()

        # Set layout for general settings tab
        self.general_settings_tab.setLayout(tab_v_box)

    def generate_local_library_info(self) -> str:
        """Generate the text to display the local library."""

        info: str = f"""
        <h3>Local library</h3>
        <p>
        Select the location of the local library. This directory will store scans for 
        syncing.
        </p>
        <p>
        <em>
        Current local library:
            <samp><a href="{self.get_library("local")}">
                {self.get_library("local")}
            </a></samp>
        </em>
        </p>
        """
        return info

    def generate_permanent_library_info(self) -> str:
        """Generate the text to display the local library."""

        info: str = f"""
        <h3>Permanent library</h3>
        <p>
        Select the location of the permanent library. This is the server that stores the raw project and scan files.
        </p>
        <p>
        <em>
        Current permanent library:
            <samp><a href="{self.get_library("permanent")}">
                {self.get_library("permanent")}
            </a></samp>
        </em>
        </p>
        """
        return info

    def open_library(self, lib_path: str, lib_title: str) -> None:
        """Open the local library directory in the file explorer."""

        if lib_path:
            QDesktopServices.openUrl(lib_path)
        else:
            QMessageBox.warning(
                self,
                f"No {lib_title} library set",
                f"No {lib_title} library set. Please set a {lib_title} library first.",
            )

    def get_library(self, library_title: str) -> str | None:
        """Get the current library to present to the user."""

        current_lib = get_value_from_toml(
            settings.general, "storage", f"{library_title}_library"
        )
        if current_lib:
            return current_lib
        return None

    def database_settings(self) -> None:
        """Database settings widget to allow the user to set the database connection."""

        if not settings.database.is_file():
            # Create a database config file if one does not already exist
            template_db_config: dict[str, dict[str, str]] = {
                "postgresql": {
                    "host": "",
                    "port": "5432",
                    "database": "",
                    "user": "",
                    "password": "",
                }
            }
            create_toml(settings.database, template_db_config)
        database_config = get_dict_from_toml(settings.database)

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
        self.test_btn = QPushButton(self)
        self.test_btn.setText("Test connection")
        self.test_btn.setToolTip("Test the database connection")
        self.test_btn.clicked.connect(self.test_db_connection)

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
        tab_v_box.addWidget(self.test_btn)
        tab_v_box.addStretch()

        # Set layout for general settings tab
        self.database_settings_tab.setLayout(tab_v_box)

    def edit_library(self, lib_title: str) -> None:
        """Open a file dialog to select the library directory."""

        if self.get_library(lib_title):
            initial_directory: str = self.get_library(lib_title)
        else:
            # Use current directory if no library is set
            initial_directory = ""

        library = QFileDialog.getExistingDirectory(
            self,
            caption=f"Select {lib_title} library directory",
            dir=initial_directory,
            options=QFileDialog.Option.ShowDirsOnly,
        )
        if library:
            update_toml(
                settings.general,
                "storage",
                f"{lib_title}_library",
                library,
            )
        else:
            logging.info("User cancelled file dialog")
            QMessageBox.warning(
                self,
                f"No {lib_title} library set",
                f"No {lib_title} library set. Please set a {lib_title} library first.",
            )

        # Update the library info text
        if lib_title == "local":
            self.local_library_info.setText(self.generate_local_library_info())
        elif lib_title == "permanent":
            self.permanent_library_info.setText(self.generate_permanent_library_info())
        else:
            logging.critical("Invalid library title: %s", lib_title)

    def apply(self) -> None:
        """Apply the changes to settings."""

        # TODO: changes to the local library should be applied not immediately;
        #  refactor under this method!

        def update_if_modified(line_edit: QLineEdit, key: str) -> None:
            """Update the config dict if the line edit has been modified."""

            if line_edit.isModified():
                update_toml(settings.database, "postgresql", key, line_edit.text())

        update_if_modified(self.host_edit, "host")
        update_if_modified(self.port_edit, "port")
        update_if_modified(self.name_edit, "database")
        update_if_modified(self.user_edit, "user")
        update_if_modified(self.password_edit, "password")

    def test_db_connection(self) -> None:
        """Test the database connection."""

        try:
            if not settings.database.is_file():
                raise FileNotFoundError
            database_config_dict = get_dict_from_toml(settings.database)
            database_config = dict_to_conn_str(database_config_dict)
            with Database(database_config) as database:
                QMessageBox.information(
                    self,
                    "Connection success",
                    "<p>Connected to database successfully.</p>"
                    f"<p>Version: <samp>{database}</samp></p>",
                    QMessageBox.StandardButton.Ok,
                )

        except psycopg.OperationalError:
            logging.exception("Exception raised")
            QMessageBox.critical(
                self,
                "Database config incorrect",
                "Check database config settings are correct.",
                QMessageBox.StandardButton.Cancel,
            )

        except FileNotFoundError:
            logging.exception("Exception raised")
            QMessageBox.critical(
                self,
                f"Database config file not found at {settings.database}",
                "Check database config settings have been saved.",
                QMessageBox.StandardButton.Cancel,
            )

        except TypeError:
            logging.exception("Exception raised")
            QMessageBox.critical(
                self,
                "Database config file type error",
                "Check database config settings are saved as the correct data type.",
                QMessageBox.StandardButton.Cancel,
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingsWindow()
    sys.exit(app.exec())
