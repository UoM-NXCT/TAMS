"""Custom database exceptions and decorator to handle database exceptions with a GUI."""

from __future__ import annotations

import logging
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

from psycopg import errors
from PySide6.QtWidgets import QMessageBox, QWidget

if TYPE_CHECKING:
    from collections.abc import Callable


class MissingTablesError(Exception):
    """Exception raised upon missing tables."""

    def __init__(
        self: MissingTablesError,
        missing_tables: set[tuple[str]],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize the exception."""
        super().__init__(*args, **kwargs)
        self._missing_tables: set[tuple[str]] = missing_tables

    def __str__(self: MissingTablesError) -> str:
        """Return a string representation of the exception."""
        return f"Database is missing the following tables: {self._missing_tables}"


if TYPE_CHECKING:
    # ParamSpec and TypeVar allow the decorator to accept any function
    P = ParamSpec("P")
    R = TypeVar("R")


def exc_gui(func: Callable[P, R]) -> Callable[P, R]:
    """Decorate database interaction functions to handle exceptions."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """Execute function and display exceptions in dialogue window."""
        try:
            return func(*args, **kwargs)
        except errors.Error as exc:
            logging.exception("Exception occurred in database interaction function.")
            QMessageBox.critical(QWidget(), "Database error", f"Exception: {exc}")

    return wrapper
