"""
Abstract runner class.
"""

import time

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerKilledException(Exception):
    """Exception raised when a worker is killed."""

    def __init__(self, message="Worker has been killed."):
        super().__init__(message)


class WorkerSignals(QObject):
    """Worker signals."""

    progress: Signal = Signal(int)
    finished: Signal = Signal()
    kill: Signal = Signal()


class AbstractJobRunner(QRunnable):
    """Abstract job runner."""

    signals: WorkerSignals = WorkerSignals()

    def __init__(self) -> None:
        super().__init__()
        self.is_paused: bool = False
        self.is_killed: bool = False
        self.is_finished: bool = False
        self.max_progress: int = 100

    @Slot()
    def run(self) -> None:
        """Perform the job."""

        while True:
            self.job()

            while self.is_paused:
                # Wait for a resume; release the GIL, so the loop does not hog the CPU.
                # Without this, the loop will waste resources doing nothing!
                time.sleep(0)
            if self.is_killed:
                # Break loop
                raise WorkerKilledException

    def job(self):
        """To be implemented by subclasses."""

        raise NotImplementedError("Runner subclass must implement this method.")

    def pause(self) -> None:
        """Pause the job."""

        self.is_paused = True

    def resume(self) -> None:
        """Resume the job."""

        self.is_paused = False

    def kill(self) -> None:
        """Kill the job."""

        self.is_killed = True
        self.signals.kill.emit()

    def finish(self) -> None:
        """Finish the job."""

        self.is_finished = True
        self.signals.finished.emit()
