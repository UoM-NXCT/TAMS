"""
This file contains custom database exceptions.

It also contains a decorator that can be used to handle database exceptions with a GUI.
"""
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from psycopg import errors
from PySide6.QtWidgets import QMessageBox, QWidget


class MissingTables(Exception):
    """Exception raised upon missing tables."""

    def __init__(self, missing_tables: set[tuple[str]], *args: tuple[Any, ...]) -> None:
        super().__init__(*args)
        self._missing_tables: set[tuple[str]] = missing_tables

    def __str__(self) -> str:
        """Return a string representation of the exception."""

        return f"Database is missing the following tables: {self._missing_tables}"


def exc_gui(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorates database interaction functions to handle exceptions."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Attempt to execute the database interaction function, and handle any exceptions
        by displaying them in a dialogue.
        """

        try:
            # Run the function
            func(*args, **kwargs)
        except errors.Error as exc:
            logging.exception("Exception occurred in database interaction function.")
            QMessageBox.critical(QWidget(), "Database error", f"Exception: {exc}")

    return wrapper
