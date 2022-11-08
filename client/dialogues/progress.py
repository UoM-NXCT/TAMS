import sys
import time

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from client.runners.abstract import AbstractJobRunner


class ProgressDialogue(QDialog):
    """Progress dialogue."""

    def __init__(self, runner: AbstractJobRunner):
        """Initialize the dialogue.

        :param runner: the job runner.
        """

        super().__init__()

        # Create the layout
        layout = QHBoxLayout()

        # Create buttons
        btn_stop = QPushButton("Stop")
        btn_pause = QPushButton("Pause")
        btn_resume = QPushButton("Resume")
        layout.addWidget(btn_stop)
        layout.addWidget(btn_pause)
        layout.addWidget(btn_resume)

        # Create the progress bar
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Set the layout
        self.setLayout(layout)

        # Thread runner
        self.threadpool = QThreadPool()

        # Create a runner
        self.runner = runner
        self.runner.signals.progress.connect(self.update_progress)
        self.threadpool.start(self.runner)

        # Connect the buttons
        btn_stop.pressed.connect(self.runner.kill)
        btn_pause.pressed.connect(self.runner.pause)
        btn_resume.pressed.connect(self.runner.resume)

        # Update progress bar
        self.progress.setRange(0, self.runner.max_progress)

        self.show()

    def update_progress(self, value_increment: int) -> None:
        """Update the progress bar."""

        value: int = self.progress.value()
        self.progress.setValue(value + value_increment)
