"""
Progress bar dialogue for downloading the scan.
"""
import logging

from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QProgressBar,
    QPushButton,
)

from client.runners.save import DownloadScansWorker


class SaveFilesDialogue(QDialog):
    """Progress dialogue."""

    def __init__(
        self,
        runner: DownloadScansWorker,
        hide: bool = False,
    ) -> None:
        """Initialize the dialogue."""

        super().__init__()

        self.setWindowTitle("Downloading data...")

        # Create the layout
        layout: QHBoxLayout = QHBoxLayout()

        # Create buttons
        btn_stop: QPushButton = QPushButton("Stop")
        btn_pause: QPushButton = QPushButton("Pause")
        btn_resume: QPushButton = QPushButton("Resume")
        layout.addWidget(btn_stop)
        layout.addWidget(btn_pause)
        layout.addWidget(btn_resume)

        # Create the progress bar
        self.progress: QProgressBar = QProgressBar()
        layout.addWidget(self.progress)

        # Set the layout
        self.setLayout(layout)

        # Thread runner
        self.threadpool: QThreadPool = QThreadPool()

        # Create a runner
        self.runner: DownloadScansWorker = runner
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

        # Pause the runner if not paused already
        if not self.runner.is_paused:
            self.runner.pause()

        # Show a message box
        QMessageBox.information(
            self,
            "Scans downloaded",
            "Scans downloaded successfully.",
        )

        # Kill the runner on job done if not killed already
        if not self.runner.is_killed:
            self.runner.kill()

        self.close()

    def closeEvent(self, arg__1: QCloseEvent) -> None:
        """Kill runner when the dialogue is closed.

        Overloads QDialog.closeEvent method.
        """

        logging.info("Closing %s.", self.__class__.__name__)

        # Kill the runner on close if not killed already
        if not self.runner.is_killed:
            self.runner.kill()

        super().closeEvent(arg__1)