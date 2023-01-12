"""
Define a table view used in the GUI.

The view gets references to items of item from the model.
"""

from PySide6.QtWidgets import QTableView


class TableView(QTableView):
    """Define the custom table view, a subclass of a built-in Qt table view."""

    # FIXME: this custom class used to do something. Now it is needed no longer. It will
    #  remain despite doing nothing in case we need to add it back. However, if it
    #  becomes clear that will not be the case, just delete and refactor!
    pass
