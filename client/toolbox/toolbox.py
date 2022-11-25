"""
Custom toolbox class that inherits the Qt built-in QToolBox widget.
"""

from PySide6.QtWidgets import QPushButton, QToolBox, QVBoxLayout, QWidget


class ToolBox(QToolBox):
    """Custom toolbox class that inherits from the Qt QToolBox built-in class."""

    def __init__(self) -> None:
        super().__init__()

        # Create project tab
        prj_tab_layout: QVBoxLayout = QVBoxLayout()
        self.prj_btn: QPushButton = QPushButton("Display projects", self)
        self.prj_btn.setToolTip("Display projects")
        prj_tab_layout.addWidget(self.prj_btn)
        self.create_prj_btn: QPushButton = QPushButton("Create project", self)
        self.create_prj_btn.setToolTip("Create a new project")
        prj_tab_layout.addWidget(self.create_prj_btn)
        prj_tab: QWidget = QWidget()
        prj_tab.setLayout(prj_tab_layout)
        self.addItem(prj_tab, "Projects")

        # Create scans tab
        scans_tab_layout: QVBoxLayout = QVBoxLayout()
        self.scans_btn: QPushButton = QPushButton("Display scans", self)
        self.scans_btn.setToolTip("Display scans")
        scans_tab_layout.addWidget(self.scans_btn)
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
