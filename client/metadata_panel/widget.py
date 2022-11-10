"""
Custom widget class inherits the Qt built-in QWidget.

Contains the metadata on the current entry; displayed on the right panel.
"""
from collections import namedtuple
from datetime import date
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import (
    QLabel,
    QLayout,
    QSplitter,
    QTableView,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client import settings
from client.thumbnails.model import PreviewDelegate, PreviewModel


class MetadataPanel(QWidget):
    """Display metadata on current selection."""

    def __init__(self) -> None:
        super().__init__()

        # Start with empty data
        self._data: tuple[Any] | None = None
        self._column_headers: list[str] | None = None

        # Create the layout
        metadata_layout: QLayout = QVBoxLayout()
        splitter: QSplitter = QSplitter(Qt.Vertical)

        # Create the thumbnail widget
        # Create a custom namedtuple class to hold our data.
        self.preview = namedtuple("preview", "id title image")
        self.thumbnail_view = QTableView()
        self.thumbnail_view.horizontalHeader().hide()
        self.thumbnail_view.verticalHeader().hide()
        self.thumbnail_view.setGridStyle(Qt.NoPen)
        self.thumbnail_view.set
        delegate = PreviewDelegate()
        self.thumbnail_view.setItemDelegate(delegate)
        self.thumbnail_model = PreviewModel()
        self.thumbnail_view.setModel(self.thumbnail_model)
        splitter.addWidget(self.thumbnail_view)

        # Add placeholder image to thumbnail widget
        images = (settings.placeholder_image,)
        for n, fn in enumerate(images):
            image = QImage(fn)
            item = self.preview(n, fn, image)
            self.thumbnail_model.previews.append(item)
        self.thumbnail_model.layoutChanged.emit()
        self.thumbnail_view.resizeRowsToContents()
        self.thumbnail_view.resizeColumnsToContents()

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

            items: list = []

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

    def update_metadata(self, metadata: tuple[tuple[Any], list[str]]) -> None:
        """Update metadata variables and tell panel to update itself."""

        self._data, self._column_headers = metadata
        self.update_content()
