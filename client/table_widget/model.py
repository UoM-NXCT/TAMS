"""
Define a table model used in the GUI.

The model handles providing the data for display by the view. We write a custom model
which is a subclass of QAbstractTableModel.

The reason for using a custom model over the built-in models is for greater control over
data representation.

Note: some PySide6 methods have bad type hints. When overloading methods, I have used
the type hints from the base class even though they are incorrect. This does not affect
the runtime behaviour of the code.
"""

import logging
from datetime import date, datetime
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt


class TableModel(QAbstractTableModel):
    """Define the custom table model, a subclass of a built-in Qt abstract model."""

    def __init__(self, data: list[tuple], column_headers: tuple[str]) -> None:
        super().__init__()
        # Anticipate a list of tuples, as this is what database returns upon select.
        self._data = data or []
        self._column_headers = column_headers or []

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = ...,  # Yes, an ellipsis is not an int. This is a PySide6 bug.
    ) -> Any:
        """Returns presentation information for given locations in the table."""

        if role == Qt.DisplayRole:
            # Get the raw value
            # .row() indexes the outer list; .column() indexes the sub-list
            value = self._data[index.row()][index.column()]

            # Perform per-type run_checks and render accordingly.
            if isinstance(value, (datetime, date)):
                # Render time to YYY-MM-DD
                return f"{value:%Y-%m-%d}"
            if isinstance(value, float):
                # Render float to 2 decimal places
                return f"{value:.2f}"
            if isinstance(value, (str, int)):
                # If it is a string or int, just render its string representation.
                return f"{value}"

            # If we get here, we have an unhandled type. Return it as-is.
            return value

            # Value was not captured above
            return f"Unknown value type: {type(value)}"

        if role == Qt.TextAlignmentRole:
            value: Any = self._data[index.row()][index.column()]

            if isinstance(value, (int, float)):
                # Align numbers to the right and vertically centre
                return Qt.AlignRight | Qt.AlignVCenter

    def rowCount(self, *args, **kwargs) -> int:
        """Return the length of the outer list."""

        return len(self._data)

    def columnCount(self, *args, **kwargs) -> int:
        """Take the first sub-list and return the length.

        This only works if all the rows are of equal length!
        """

        return len(self._data[0])

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = ...,  # Yes, an ellipsis is not an int. This is a PySide6 bug.
    ) -> Any:
        """Return the header data."""

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                header: str = str(self._column_headers[section])
                return header

        # Not returning this makes headers not show, for whatever reason.
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def get_row_data(self, row_index: int) -> tuple[Any, ...]:
        """Return the row from a given row index."""
        return self._data[row_index]
