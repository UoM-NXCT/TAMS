"""
Custom widget class inherits the Qt built-in QWidget.

Contains the metadata on the current entry; displayed on the right panel.
"""
from datetime import date
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLayout,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client import settings
from client.thumbnail.model import ThumbnailWidget

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

        metadata_layout.addWidget(splitter)

        # Set the layout
        self.setLayout(metadata_layout)

        # Set the initial content
        self.update_content()

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

    def update_thumbnail(self) -> None:
        """Update the thumbnail widget."""

        if self._data and self._column_headers:

            # Get the project ID
            try:
                project_id: int | str | None = self._data[
                    self._column_headers.index("project_id")
                ]
                if isinstance(project_id, str):
                    # If the project ID is a string, it is of tge form "project_id (title)"
                    # Get the first word and convert it to an integer to get the project ID
                    project_id = int(project_id.split()[0])
            except ValueError:
                # If the project ID is not found, set it to None
                project_id = None

            # Get the scan ID
            try:
                scan_id: int | str | None = self._data[
                    self._column_headers.index("scan_id")
                ]
                if isinstance(scan_id, str):
                    # If the scan ID is a string, it is of tge form "scan_id (title)"
                    # Get the first word and convert it to an integer to get the scan ID
                    scan_id = int(scan_id.split()[0])
            except ValueError:
                # If the scan ID is not found, set it to None
                scan_id = None

            if project_id:
                # If both the project ID and scan ID are found, load the thumbnail
                thumbnail: Path = get_thumbnail(project_id, scan_id)
                self.thumbnail_widget.load(thumbnail)
            else:
                self.thumbnail_widget.load(settings.placeholder_image)

    def update_metadata(self, metadata: tuple[tuple[Any], list[str]]) -> None:
        """Update metadata variables and tell panel to update itself."""

        self._data, self._column_headers = metadata
        self.update_content()
        self.update_thumbnail()
