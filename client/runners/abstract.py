"""
Abstract runner class.
"""

import time

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerKilledException(Exception):
    """Exception raised when a worker is killed."""

    pass


class WorkerSignals(QObject):
    """Worker signals."""

    progress = Signal(int)


class AbstractJobRunner(QRunnable):
    """Abstract job runner."""

    signals: WorkerSignals = WorkerSignals()

    def __init__(self) -> None:
        super().__init__()
        self.is_paused: bool = False
        self.is_killed: bool = False
        self.max_progress: int = 100

    @Slot()
    def run(self) -> None:
        """Perform the job."""

        while not self.is_killed and not self.is_paused:
            self.job()

            while self.is_paused:
                time.sleep(0.1)
            if self.is_killed:
                raise WorkerKilledException

    def job(self):
        """To be implemented by subclasses."""
        ...

    def pause(self) -> None:
        """Pause the job."""

        self.is_paused = True

    def resume(self) -> None:
        """Resume the job."""

        self.is_paused = False

    def kill(self) -> None:
        """Kill the job."""

        self.is_killed = True
