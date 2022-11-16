import sys
import time
import traceback
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class WorkerSignals(QObject):
    """Worker signals."""

    finished: Signal = Signal()
    error: Signal = Signal(tuple)
    result: Signal = Signal(object)


class Worker(QRunnable):
    """Worker thread

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.

    :param callback: the function callback to run on this worker thread. Supplied args and
        kwargs will be passed through to the runner.
    :param args: arguments to pass to the callback function.
    :param kwargs: keyword to pass to callback function.
    """

    def __init__(self, fn: Callable, *args: Any, **kwargs: Any):
        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn: Callable = fn
        self.args: tuple[Any, ...] = args
        self.kwargs: dict[str, Any] = kwargs
        self.signals: WorkerSignals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        """Initialise the runner function with passed args, kwargs."""

        try:
            result: Any = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit() # Done