"""
Model for the thumbnail widget.
"""

import math
from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    Qt,
)
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem


class PreviewDelegate(QStyledItemDelegate):
    """A custom delegate to draw the thumbnails."""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the thumbnail."""

        # data is our preview object
        data = index.model().data(index, Qt.DisplayRole)
        if data is None:
            return

        cell_padding: int = 0  # all sides

        # option.rect holds the area we are painting on the widget (our table cell)
        width: int = option.rect.width() - cell_padding * 2
        height: int = option.rect.height() - cell_padding * 2

        # Scale our pixmap thumbnail to fit
        scaled: QImage = data.image.scaled(
            width,
            height,
            Qt.KeepAspectRatio,
        )

        # Position the image in the center of the cell
        x: float = cell_padding + (width - scaled.width()) / 2
        y: float = cell_padding + (height - scaled.height()) / 2

        painter.drawImage(option.rect.x() + x, option.rect.y() + y, scaled)

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        """Return the size of the thumbnail."""

        # All items the same size.
        return QSize(200, 200)


class PreviewModel(QAbstractTableModel):
    """Use a table view to display the thumbnails.

    Hence, we can display multiple thumbnails, though we only display one currently.
    """

    def __init__(self):
        super().__init__()
        # .data holds our data for display, as a list of Preview objects.
        self.previews = []
        self.number_of_columns = 1

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = ...,  # Yes, an ellipsis is not an int. This is a PySide6 bug.
    ) -> Any:
        try:
            data = self.previews[index.row() * self.number_of_columns + index.column()]
        except IndexError:
            # Incomplete last row.
            return

        if role == Qt.DisplayRole:
            return data  # Pass the data to our delegate to draw.

        if role == Qt.ToolTipRole:
            return data.title

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        return self.number_of_columns

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        number_of_items: int = len(self.previews)
        return math.ceil(number_of_items / self.number_of_columns)
