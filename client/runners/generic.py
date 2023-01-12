"""
Generic worker class for running jobs in a separate thread.
"""

import logging
import sys
import traceback
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

if TYPE_CHECKING:
    from collections.abc import Callable


class RunnerKilledException(Exception):
    """Exception raised when a runner is killed."""

    def __init__(self, msg: str = "Worker has been killed."):
        super().__init__(msg)


class RunnerFinishedException(Exception):
    """Exception raised when a runner is finished."""

    def __init__(self, msg: str = "Worker has finished."):
        super().__init__(msg)


class RunnerStatus(Enum):
    """Enum for runner status flags."""

    RUNNING = auto()
    PAUSED = auto()
    KILLED = auto()
    FINISHED = auto()


class RunnerSignals(QObject):
    """Worker signals."""

    finished: Signal = Signal()
    kill: Signal = Signal()
    progress: Signal = Signal(int)
    error: Signal = Signal(tuple)
    result: Signal = Signal(object)


class GenericRunner(QRunnable):
    """Generic runner thread

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    """

    def __init__(self, func: Callable[[], Any]):
        """Initialize the worker."""

        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn: Callable[[], Any] = func

        self.signals: RunnerSignals = RunnerSignals()

        # Status flags
        self.worker_status: RunnerStatus = RunnerStatus.RUNNING

        self.result_value: Any = None

        # By default, progress is out of 100
        self._max_progress: int = 100

    @Slot()
    def run(self) -> None:
        """Initialize the runner function with passed args, kwargs."""

        try:
            result: Any = self.fn()
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
        """Set the max progress of the runner."""

        if isinstance(max_progress, int) and (max_progress > 0):
            self._max_progress = max_progress
        else:
            raise TypeError("max progress must be a positive integer.")

    def get_max_progress(self) -> int:
        """Get the max progress of the runner."""

        return self._max_progress

    def kill(self) -> None:
        """Kill the runner."""

        logging.info("%s killed.", self.__class__.__name__)
        self.worker_status = RunnerStatus.KILLED
        self.signals.kill.emit()

    def pause(self) -> None:
        """Pause the runner."""

        logging.info("%s paused.", self.__class__.__name__)
        self.worker_status = RunnerStatus.PAUSED

    def resume(self) -> None:
        """Resume the runner."""

        logging.info("%s resumed.", self.__class__.__name__)
        self.worker_status = RunnerStatus.RUNNING

    def finish(self) -> None:
        """Finish the runner."""

        logging.info("%s finished.", self.__class__.__name__)
        self.worker_status = RunnerStatus.FINISHED
        self.signals.finished.emit()

    def set_result(self, result: Any) -> None:
        """Set the result of the runner and finish."""

        logging.info("%s result set: %s", self.__class__.__name__, result)
        self.result_value = result
        self.signals.result.emit(result)
        self.finish()
