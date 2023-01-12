# Widgets

The widget is the atom of the user interface: it receives mouse, keyboard and other events from the window system and paints a representation of itself on the screen.

`QWidget` has many member functions, but some have little direct functionality. Many subclasses provide extra functionality, such as `QLabel` and `QPushButton`.

This project uses custom widgets not built-in to extend the functionality of Qt6. These are located in the `/widgets` directory.

Official documentation (GNU FDL v1.3):

- [Qt6](https://doc.qt.io/qt-6/qwidget.html)
- [PySide6](https://doc.qt.io/qtforpython/PySide6/QtWidgets/QWidget.html)

Tutorials:

- [Martin Fitzpatrick](https://www.pythonguis.com/tutorials/pyside6-widgets/)

## Dialogues

A dialogue is a type of widget.

A dialogue window is a top-level window mostly used for short-term tasks and brief communications with the user. They may be modal (block input to other app windows). A dialogue is always a top-level widget, but if it has a parent, its default location is centred over the parent’s top-level widget (if it is not top-level itself). It will also share the parent’s taskbar entry.

Custom dialogues are located in the `/widgets/dialogue` directory.

Note: Qt6 uses the American spelling: dialog. I have used the British spelling (dialogue) to delineate where Qt6 code ends and new code begins.
