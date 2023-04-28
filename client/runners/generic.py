"""Generic worker class for running jobs in a separate thread."""
from __future__ import annotations

import logging
import sys
import traceback
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

if TYPE_CHECKING:
    from collections.abc import Callable


class RunnerKilledException(Exception):  # noqa: N818
    """Exception raised when a runner is killed."""

    def __init__(
        self: RunnerKilledException, msg: str = "Worker has been killed."
    ) -> None:
        """Initialize the exception."""
        super().__init__(msg)


class RunnerFinishedException(Exception):  # noqa: N818
    """Exception raised when a runner is finished."""

    def __init__(
        self: RunnerFinishedException, msg: str = "Worker has finished."
    ) -> None:
        """Initialize the exception."""
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
    """Generic runner thread.

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    """

    def __init__(self: GenericRunner, func: Callable[[], Any]) -> None:
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
    def run(self: GenericRunner) -> None:
        """Initialize the runner function with passed args, kwargs."""
        try:
            result: Any = self.fn()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()  # Done

    def set_max_progress(self: GenericRunner, max_progress: int) -> None:
        """Set the max progress of the runner."""
        if isinstance(max_progress, int) and (max_progress > 0):
            self._max_progress = max_progress
        else:
            msg = f"max progress must be a positive integer, not {max_progress}"
            raise TypeError(msg)

    def get_max_progress(self: GenericRunner) -> int:
        """Get the max progress of the runner."""
        return self._max_progress

    def kill(self: GenericRunner) -> None:
        """Kill the runner."""
        logging.info("%s killed.", self.__class__.__name__)
        self.worker_status = RunnerStatus.KILLED
        self.signals.kill.emit()

    def pause(self: GenericRunner) -> None:
        """Pause the runner."""
        logging.info("%s paused.", self.__class__.__name__)
        self.worker_status = RunnerStatus.PAUSED

    def resume(self: GenericRunner) -> None:
        """Resume the runner."""
        logging.info("%s resumed.", self.__class__.__name__)
        self.worker_status = RunnerStatus.RUNNING

    def finish(self: GenericRunner) -> None:
        """Finish the runner."""
        logging.info("%s finished.", self.__class__.__name__)
        self.worker_status = RunnerStatus.FINISHED
        self.signals.finished.emit()

    def set_result(self: GenericRunner, result: bool) -> None:
        """Set the result of the runner and finish."""
        logging.info("%s result set: %s", self.__class__.__name__, result)
        self.result_value = result
        self.signals.result.emit(result)
        self.finish()
