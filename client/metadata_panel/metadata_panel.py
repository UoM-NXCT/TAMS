"""Metadata panel

Custom widget class that inherits the Qt built-in QWidget. Contains the metadata on the current entry; displayed on
the left panel.
"""
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
        self.data: tuple[Any] | None = None
        self.column_headers: list[str] | None = None
        metadata_layout: QLayout = QVBoxLayout()
        self.metadata_tree = QTreeWidget()
        self.metadata_tree.setColumnCount(1)
        self.metadata_tree.setHeaderHidden(True)
        metadata_layout.addWidget(self.metadata_tree)
        self.setLayout(metadata_layout)
        self.update_content()

    def update_content(self) -> None:
        """Update the metadata panel content."""

        self.metadata_tree.clear()

        if self.data and self.column_headers:
            items = []
            for index, column in enumerate(self.column_headers):
                item = QTreeWidgetItem([column])
                values: Any = self.data[index]
                # TODO: there has to be a nicer way of doing this!
                if isinstance(values, str):
                    child = QTreeWidgetItem([values])
                    item.addChild(child)
                else:
                    for value in values:
                        child = QTreeWidgetItem([value])
                        item.addChild(child)

                items.append(item)
            self.metadata_tree.insertTopLevelItems(0, items)
            self.metadata_tree.expandAll()
        else:
            pass

    def update_metadata(self, metadata: tuple[tuple[Any], list[str]]) -> None:
        """Update metadata variables and tell panel to update itself."""

        self.data, self.column_headers = metadata
        self.update_content()
