"""
The thumbnail widget scales an image to fill a box while maintaining aspect ratio.
"""

from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPalette, QPixmap, QResizeEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class ThumbnailWidget(QFrame):
    """A widget that scales an image to fill a box while maintaining aspect ratio."""

    def __init__(self) -> None:
        super().__init__()

        # Use a layout to prevent the image from being stretched
        layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(layout)

        # Create a label to display the image
        self.label: QLabel = QLabel()

        # Center the image in the label
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the label to the layout
        layout.addWidget(self.label)

        # Set the letterbox/pillarbox colour to black
        pal: QPalette = self.palette()
        pal.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        # No black borders around non-letterboxed/pillarboxed images
        layout.setContentsMargins(0, 0, 0, 0)

        self.original_pixmap: QPixmap = QPixmap()

    def load(self, source: Path) -> None:
        """Load an image from a file and display it in the thumbnail.

        This is not an overload. It is a custom method.
        """

        self.original_pixmap = QPixmap(source)
        self.label.setPixmap(self.original_pixmap)
        self.setToolTip(str(source.absolute()))

        # Keep Qt from preventing the image from being scaled down
        self.setMinimumSize(1, 1)

        # Force a resize event to update the image to fit the thumbnail
        _arbitrary_event: QResizeEvent = QResizeEvent(self.size(), self.size())
        self.resizeEvent(_arbitrary_event)

    def resizeEvent(self, _event: QResizeEvent) -> None:
        """Resize handler to update the dimensions of the displayed image.

        Overloads parent resizeEvent method.
        """

        rect: QRect = self.geometry()

        size: QSize = QSize(rect.width(), rect.height())

        # Scale the image to fit the thumbnail
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.label.setPixmap(
                self.original_pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio)
            )

            # Don't waste time generating a new pixmap if it didn't alter its bounds
            pixmap_size: QSize = self.label.pixmap().size()
            if (pixmap_size.width() == size.width()) and (
                pixmap_size.height() <= size.height()
            ):
                return
            if (pixmap_size.height() == size.height()) and (
                pixmap_size.width() <= size.width()
            ):
                return

            self.label.setPixmap(
                self.original_pixmap.scaled(
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
