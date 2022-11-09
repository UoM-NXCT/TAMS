"""
Custom toolbox class that inherits the Qt built-in QToolBox widget.
"""

from PySide6.QtWidgets import QPushButton, QToolBox, QVBoxLayout, QWidget


class ToolBox(QToolBox):
    """Custom toolbox class that inherits from the Qt QToolBox built-in class."""

    def __init__(self) -> None:
        super().__init__()

        # Create project tab
        projects_tab_layout: QVBoxLayout = QVBoxLayout()
        self.projects_button: QPushButton = QPushButton("Display projects", self)
        self.projects_button.setToolTip("Display projects")
        projects_tab_layout.addWidget(self.projects_button)
        self.create_prj_btn: QPushButton = QPushButton("Create project", self)
        self.create_prj_btn.setToolTip("Create a new project")
        projects_tab_layout.addWidget(self.create_prj_btn)
        projects_tab: QWidget = QWidget()
        projects_tab.setLayout(projects_tab_layout)
        self.addItem(projects_tab, "Projects")

        # Create scans tab
        scans_tab_layout: QVBoxLayout = QVBoxLayout()
        self.scans_button: QPushButton = QPushButton("Display scans", self)
        self.scans_button.setToolTip("Display scans")
        scans_tab_layout.addWidget(self.scans_button)
        self.create_scan_btn: QPushButton = QPushButton("Create scan", self)
        self.create_scan_btn.setToolTip("Create a new scan")
        scans_tab_layout.addWidget(self.create_scan_btn)
        scans_tab: QWidget = QWidget()
        scans_tab.setLayout(scans_tab_layout)
        self.addItem(scans_tab, "Scans")

        # Create users tab
        users_tab_layout: QVBoxLayout = QVBoxLayout()
        self.users_btn: QPushButton = QPushButton("Display users", self)
        self.users_btn.setToolTip("Display users")
        users_tab_layout.addWidget(self.users_btn)
        users_tab: QWidget = QWidget()
        users_tab.setLayout(users_tab_layout)
        self.addItem(users_tab, "Users")
