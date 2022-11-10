"""
Custom widget class that inherits the Qt built-in QWidget.

Contains the metadata on the current entry; displayed on the right panel.
"""

from datetime import date
from typing import Any

from PySide6.QtWidgets import (
    QLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MetadataPanel(QWidget):
    """Display metadata on current selection."""

    def __init__(self) -> None:
        super().__init__()

        # Start with empty data
        self._data: tuple[Any] | None = None
        self._column_headers: list[str] | None = None

        # Create the layout
        metadata_layout: QLayout = QVBoxLayout()

        # Create the tree widget
        self.metadata_tree: QTreeWidget = QTreeWidget()
        self.metadata_tree.setColumnCount(1)
        # Hide the header; our tree is vertical so there is no reason to include it.
        self.metadata_tree.setHeaderHidden(True)

        # Add the tree to the layout
        metadata_layout.addWidget(self.metadata_tree)

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
                if isinstance(values, (str, int)):
                    child: QTreeWidgetItem = QTreeWidgetItem([str(values)])
                    child.setToolTip(0, str(values))
                    item.addChild(child)
                elif isinstance(values, date):
                    child: QTreeWidgetItem = QTreeWidgetItem([str(values)])
                    child.setToolTip(0, f"{values} (YYYY-MM-DD)")
                    item.addChild(child)
                elif isinstance(values, tuple):
                    for value in values:
                        child: QTreeWidgetItem = QTreeWidgetItem([value])
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
