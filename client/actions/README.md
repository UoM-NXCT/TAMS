# Actions

Many common commands can be invoked in applications via menus, toolbar buttons, and keyboard shortcuts. Since the user expects each command to be performed the same way, regardless of the user interface used, it is useful to represent each command as an action.

Actions can be added to menus and toolbars and automatically keep them in sync. For example, if the user presses a Bold toolbar button in a word processor, the Bold menu item will automatically be checked.

Most actions have an icon, name, shortcut, tooltip, and on trigger method. For example, the UpdateTable action has a reload icon, name, shortcut (Ctrl+R), tooltip, and on trigger method (update_table) that reloads the table.

Technical documentation:

- [Qt6](https://doc.qt.io/qt-6/qaction.html)
- [PySide6](https://doc.qt.io/qtforpython/PySide6/QtGui/QAction.html)
