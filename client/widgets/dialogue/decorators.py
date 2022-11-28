import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from PySide6.QtWidgets import QMessageBox, QWidget


def attempt_file_io(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorates file operation methods with exception handling methods."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        """Attempt to execute the sql command, and handle any exceptions."""

        try:
            func(*args, **kwargs)
        except FileNotFoundError as exc:
            logging.exception("Exception raised")
            QMessageBox.critical(
                QWidget(),
                "Error: file not found",
                f"File {exc.filename} not found. "
                "Check that the file exists and is accessible.",
            )

    return wrapper
