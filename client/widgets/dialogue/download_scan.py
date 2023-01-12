"""
Progress bar dialogue for downloading the scan.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from client.runners.generic import RunnerStatus
from client.utils.file import size_fmt

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent
    from PySide6.QtWidgets import QWidget

    from client.runners.save import SaveScans


class DownloadScans(QDialog):
    """Progress dialogue."""

    def __init__(
        self,
        runner: SaveScans,
        hide: bool = False,
        parent_widget: QWidget | None = None,
    ) -> None:
        """Initialize the dialogue."""

        super().__init__(parent=parent_widget)

        self.setWindowTitle("Downloading data...")

        # Create the layout
        layout: QVBoxLayout = QVBoxLayout()
        bar_layout: QHBoxLayout = QHBoxLayout()

        # Create label
        label = QLabel(
            f"Downloading {runner.get_max_progress() + 1} items..."
            f" ({size_fmt(runner.size_in_bytes)})"
        )
        layout.addWidget(label)

        # Create buttons
        btn_stop: QPushButton = QPushButton("Stop")
        btn_pause: QPushButton = QPushButton("Pause")
        btn_resume: QPushButton = QPushButton("Resume")

        # Add buttons to layout
        bar_layout.addWidget(btn_stop)
        bar_layout.addWidget(btn_pause)
        bar_layout.addWidget(btn_resume)

        # Create the progress bar
        self.progress: QProgressBar = QProgressBar()
        bar_layout.addWidget(self.progress)

        layout.addLayout(bar_layout)

        # Set the layout
        self.setLayout(layout)

        # Thread runner
        self.threadpool: QThreadPool = QThreadPool()

        # Create a runner
        self.runner: SaveScans = runner
        self.runner.signals.progress.connect(self.update_progress)
        self.runner.signals.finished.connect(self.job_done)
        self.runner.signals.kill.connect(self.close)
        self.threadpool.start(self.runner)

        # Connect the buttons
        btn_stop.pressed.connect(self.runner.kill)
        btn_pause.pressed.connect(self.runner.pause)
        btn_resume.pressed.connect(self.runner.resume)

        # Update progress bar
        self.progress.setRange(0, self.runner.get_max_progress())

        # Show the dialogue
        if not hide:
            self.show()

    def update_progress(self, value_increment: int) -> None:
        """Update the progress bar."""

        value: int = self.progress.value()
        self.progress.setValue(value + value_increment)

    def job_done(self) -> None:
        """Show a message box when the job is done."""

        # Show a message box
        QMessageBox.information(
            self,
            "Scans downloaded",
            "Scans downloaded successfully.",
        )

        self.close()

    def closeEvent(self, arg__1: QCloseEvent) -> None:
        """Kill runner when the dialogue is closed.

        Overloads QDialog.closeEvent method.
        """

        logging.info("Closing %s.", self.__class__.__name__)

        # Kill the runner on close if not killed already
        if self.runner.worker_status is not RunnerStatus.KILLED:
            self.runner.kill()

        super().closeEvent(arg__1)
