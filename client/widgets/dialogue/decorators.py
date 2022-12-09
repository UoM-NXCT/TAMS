"""
Decoration function utilities.
"""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMessageBox, QWidget

from client.utils import log

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


def handle_common_exc(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorates methods to display exceptions graphically.

    Many exceptions are common to many methods, and can be handles simply by displaying
    a message box. This decorator handles those exceptions to avoid repetition.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        """Attempt to execute file operations, and handle any exceptions."""

        try:
            func(*args, **kwargs)
        except FileNotFoundError as exc:
            log.logger(__name__).error("File %s not found", exc.filename)
            QMessageBox.critical(
                QWidget(),
                "File not found error",
                f"File {exc.filename} not found."
                "Check that the path exists and is accessible.",
            )
        except RuntimeError as exc:
            log.logger(__name__).exception("Exception raised")
            QMessageBox.critical(
                QWidget(),
                "File operation runtime error",
                f"{exc}",
            )

    return wrapper
