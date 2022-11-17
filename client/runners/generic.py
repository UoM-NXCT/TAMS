"""
Generic worker class for running jobs in a separate thread.
"""

import logging
import sys
import traceback
from enum import Enum, auto
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerKilledException(Exception):
    """Exception raised when a worker is killed."""

    def __init__(self, message: str = "Worker has been killed."):
        super().__init__(message)


class WorkerFinishedException(Exception):
    """Exception raised when a worker is finished."""

    def __init__(self, message: str = "Worker has finished."):
        super().__init__(message)


class WorkerStatus(Enum):
    """Enum for worker status flags."""

    RUNNING = auto()
    PAUSED = auto()
    KILLED = auto()
    FINISHED = auto()


class WorkerSignals(QObject):
    """Worker signals."""

    finished: Signal = Signal()
    kill: Signal = Signal()
    progress: Signal = Signal(int)
    error: Signal = Signal(tuple)
    result: Signal = Signal(object)


class Worker(QRunnable):
    """Worker thread

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.

    :param callback: the function callback to run on this worker thread. Supplied args
        and kwargs will be passed through to the runner.
    :param args: arguments to pass to the callback function.
    :param kwargs: keyword to pass to callback function.
    """

    def __init__(self, fn: Callable, *args: Any, **kwargs: Any):
        """Initialize the worker."""

        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn: Callable = fn
        self.args: tuple[Any, ...] = args
        self.kwargs: dict[str, Any] = kwargs
        self.signals: WorkerSignals = WorkerSignals()

        # Status flags
        self.worker_status: WorkerStatus = WorkerStatus.RUNNING

        self.result_value: Any = None

        # By default, progress is out of 100
        self._max_progress: int = 100

    @Slot()
    def run(self) -> None:
        """Initialise the runner function with passed args, kwargs."""

        try:
            result: Any = self.fn(*self.args, **self.kwargs)
        except Exception:  # pylint: disable=broad-except
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()  # Done

    def set_max_progress(self, max_progress: int) -> None:
        """Set the max progress of the worker."""

        if isinstance(max_progress, int) and (max_progress > 0):
            self._max_progress = max_progress
        else:
            raise TypeError("max progress must be a positive integer.")

    def get_max_progress(self) -> int:
        """Get the max progress of the worker."""

        return self._max_progress

    def kill(self) -> None:
        """Kill the worker."""

        logging.info("%s killed.", self.__class__.__name__)
        self.worker_status = WorkerStatus.KILLED
        self.signals.kill.emit()

    def pause(self) -> None:
        """Pause the worker."""

        logging.info("%s paused.", self.__class__.__name__)
        self.worker_status = WorkerStatus.PAUSED

    def resume(self) -> None:
        """Resume the worker."""

        logging.info("%s resumed.", self.__class__.__name__)
        self.worker_status = WorkerStatus.RUNNING

    def finish(self) -> None:
        """Finish the worker."""

        logging.info("%s finished.", self.__class__.__name__)
        self.worker_status = WorkerStatus.FINISHED
        self.signals.finished.emit()

    def set_result(self, result: Any) -> None:
        """Set the result of the worker and finish."""

        logging.info("%s result set: %s", self.__class__.__name__, result)
        self.result_value = result
        self.signals.result.emit(result)
        self.finish()
