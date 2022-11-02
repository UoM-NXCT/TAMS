"""Metadata panel

Custom widget class that inherits the Qt built-in QWidget. Contains the metadata on the current entry; displayed on
the left panel.
"""
from typing import Any

from PySide6.QtWidgets import QLabel, QLayout, QVBoxLayout, QWidget


class MetadataPanel(QWidget):
    """Display metadata on current selection."""

    def __init__(self) -> None:
        super().__init__()
        self.data: tuple[Any] | None = None
        self.column_headers: list[str] | None = None
        self.metadata_label: QLabel = QLabel()
        self.metadata_label.setWordWrap(True)
        metadata_layout: QLayout = QVBoxLayout()
        metadata_layout.addWidget(self.metadata_label)
        self.setLayout(metadata_layout)
        self.update_content()

    def update_content(self) -> None:
        """Update the metadata panel content."""

        if self.data:
            self.metadata_label.setText(str(self.data))
        else:
            self.metadata_label.setText("No data selected.")

    def update_metadata(self, metadata: tuple[tuple[Any], list[str]]) -> None:
        """Update metadata variables and tell panel to update itself."""

        self.data, self.column_headers = metadata
        self.update_content()
