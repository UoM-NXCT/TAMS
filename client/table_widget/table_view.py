"""Define a table view used in the GUI.

The view gets references to items of item from the model.

The reason we use a custom table view over the built-in Qt table view is that we want
our view to react to user clicking. While this is technically possible to do using the 
built-in, moving the logic to a custom class makes the code easier to comprehend.
"""
import logging

from PySide6.QtCore import QAbstractItemModel, QItemSelection
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QTableView


class TableView(QTableView):
    """Define the custom table view, a subclass of a built-in Qt table view."""

    def __init__(self):
        """
        Initialise the view by calling the QTableView __init__ method and declaring
        custom variables.
        """
        super().__init__()
        self.selected_row: int = 0

    def update_selected_row(self) -> None:
        """Update the selected row variable to equal the row currently selected."""
        try:
            self.selected_row = self.selectedIndexes()[0].row()
        except IndexError:
            # This exception is raised when no row is selected.
            logging.exception("No row selected.")
        logging.info("Selected row: %s", self.selected_row)

    def setModel(self, model: QAbstractItemModel) -> None:
        QTableView.setModel(self, model)
        self.selectRow(0)

    def selectionChanged(
        self,
        selected: QItemSelection,
        deselected: QItemSelection,
    ) -> None:
        QTableView.selectionChanged(self, selected, deselected)
        self.update_selected_row()
