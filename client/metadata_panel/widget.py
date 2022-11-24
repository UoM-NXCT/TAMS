"""
Custom widget class inherits the Qt built-in QWidget.

Contains the metadata on the current entry; displayed on the right panel.
"""
import logging
from datetime import date
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client import settings
from client.thumbnail.model import ThumbnailWidget

from ..utils.toml import get_value_from_toml
from .thumbnail import get_thumbnail


class MetadataPanel(QWidget):
    """Display metadata on current selection."""

    def __init__(self) -> None:
        super().__init__()

        # Start with empty data
        self._data: tuple[Any] | None = None
        self._column_headers: list[str] | None = None

        # Create the layout
        metadata_layout: QLayout = QVBoxLayout()
        splitter: QSplitter = QSplitter(Qt.Orientation.Vertical)

        # Create the thumbnail widget
        self.thumbnail_widget: ThumbnailWidget = ThumbnailWidget()
        self.thumbnail_widget.load(settings.placeholder_image)
        splitter.addWidget(self.thumbnail_widget)

        # Create the tree widget
        self.metadata_tree: QTreeWidget = QTreeWidget()
        self.metadata_tree.setColumnCount(1)
        # Hide the header; our tree is vertical so there is no reason to include it.
        self.metadata_tree.setHeaderHidden(True)

        # Add the tree to the layout
        splitter.addWidget(self.metadata_tree)

        # Create README.txt widget
        self.readme_widget: QWidget = QWidget()
        readme_layout = QVBoxLayout()

        # Create the text edit
        readme_label: QLabel = QLabel("README.txt")
        self.readme_text = QTextEdit()
        self.readme_text.setReadOnly(True)
        readme_layout.addWidget(readme_label)
        readme_layout.addWidget(self.readme_text)

        # Create the text edit buttons
        btn_layout = QHBoxLayout()
        self.open_readme_btn = QPushButton("Open README.txt")
        self.open_readme_btn.clicked.connect(self.open_readme)
        btn_layout.addWidget(self.open_readme_btn)
        readme_layout.addLayout(btn_layout)

        # Add the layout to the widget
        self.readme_widget.setLayout(readme_layout)

        # Add the README.txt widget to the splitter
        splitter.addWidget(self.readme_widget)

        # Add the splitter to the layout
        metadata_layout.addWidget(splitter)

        # Set the layout
        self.setLayout(metadata_layout)

        # Set the initial content
        self.update_metadata()

    def open_readme(self):
        """Open the README.txt file."""

        logging.info("Opening README.txt")
        readme_dir: Path = self.get_readme_dir()
        readme_file: Path = readme_dir / "README.txt"
        QDesktopServices.openUrl(QUrl.fromLocalFile(readme_file))

    def update_content(self) -> None:
        """Update the metadata panel content."""

        # Clear the tree
        self.metadata_tree.clear()

        if self._data and self._column_headers:

            items: list[QTreeWidgetItem] = []

            # Iterate over the data and column headers
            for index, column in enumerate(self._column_headers):

                # Create the tree item for the column
                item: QTreeWidgetItem = QTreeWidgetItem([column])

                # Get the values for this column
                values: Any = self._data[index]

                # Render and add the values to the tree item
                child: QTreeWidgetItem
                if isinstance(values, (str, int, date)):
                    child = QTreeWidgetItem([str(values)])
                    if isinstance(values, date):
                        child.setToolTip(0, f"{values} (YYYY-MM-DD)")
                    else:
                        child.setToolTip(0, str(values))
                    item.addChild(child)
                elif isinstance(values, tuple):
                    # TODO: this is a hack; try to find a better way to handle this.
                    for value in values:
                        child = QTreeWidgetItem([value])
                        child.setToolTip(0, value)
                        item.addChild(child)

                # Add tree item to the tree items list
                items.append(item)

            # Add the tree items to the tree
            self.metadata_tree.insertTopLevelItems(0, items)

            # Expand the tree to show all items by default
            self.metadata_tree.expandAll()

    def get_project_id(self):
        """Get the project ID from the metadata."""
        try:
            project_id: int | str | None = self._data[
                self._column_headers.index("project_id")
            ]
            if isinstance(project_id, str):
                # If the project ID is a string, it is of tge form "project_id (title)"
                # Get the first word and convert it to an integer to get the project ID
                project_id = int(project_id.split()[0])
        except ValueError:
            project_id = None

        return project_id

    def get_scan_id(self):
        """Get the scan ID from the metadata."""
        try:
            scan_id: int | str | None = self._data[
                self._column_headers.index("scan_id")
            ]
            if isinstance(scan_id, str):
                # If the scan ID is a string, it is of tge form "scan_id (title)"
                # Get the first word and convert it to an integer to get the scan ID
                scan_id = int(scan_id.split()[0])
        except ValueError:
            scan_id = None

        return scan_id

    def update_thumbnail(self) -> None:
        """Update the thumbnail widget."""

        if self._data and self._column_headers:

            # Get the project ID
            project_id: int | None = self.get_project_id()

            # Get the scan ID
            scan_id: int | None = self.get_scan_id()

            if project_id:
                # If the project ID is found, load the thumbnail
                thumbnail: Path = get_thumbnail(project_id, scan_id)
                self.thumbnail_widget.load(thumbnail)
            else:
                self.thumbnail_widget.load(settings.placeholder_image)

    def update_readme_text_edit(self, readme_dir: Path) -> None:
        """Load the README.txt file."""

        readme_file: Path = readme_dir / "README.txt"
        if readme_file.exists():
            with open(readme_file, encoding="utf-8") as f:
                readme: str = f.read()
            self.readme_text.setText(readme)
        else:
            raise FileNotFoundError(f"README.txt not found in {readme_dir}")

    def get_readme_dir(self) -> Path:
        """Get the README.txt file."""

        # Get the project ID
        project_id: int | None = self.get_project_id()

        # Get the scan ID
        scan_id: int | None = self.get_scan_id()

        local_lib: Path = Path(
            get_value_from_toml(settings.general, "storage", "local_library")
        )

        if project_id and scan_id:
            return local_lib / str(project_id) / str(scan_id) / "tams_meta"
        elif project_id and not scan_id:
            return local_lib / str(project_id) / "tams_meta"
        else:
            raise ValueError("Project ID not found.")

    def update_readme(self) -> None:
        """Update the README.txt widget."""

        if self._data and self._column_headers:

            readme_dir: Path = self.get_readme_dir()

            try:
                self.update_readme_text_edit(readme_dir)
                self.readme_widget.show()
            except FileNotFoundError:
                logging.info(f"README.txt not found in {readme_dir}")
                self.readme_widget.hide()
        else:
            self.readme_widget.hide()

    def update_metadata(
        self,
        metadata: tuple[tuple[Any], list[str]]
        | tuple[None, None] = (
            None,
            None,
        ),
    ) -> None:
        """Update metadata variables and tell panel to update itself."""

        self._data, self._column_headers = metadata
        self.update_content()
        self.update_thumbnail()
        self.update_readme()
