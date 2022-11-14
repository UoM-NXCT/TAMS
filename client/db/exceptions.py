"""
This file contains custom database exceptions.
"""
from typing import Any


class MissingTables(Exception):
    """Exception raised upon missing tables."""

    def __init__(self, missing_tables: set[tuple[str]], *args: tuple[Any, ...]) -> None:
        super().__init__(*args)
        self._missing_tables: set[tuple[str]] = missing_tables

    def __str__(self) -> str:
        return f"Database is missing the following tables: {self._missing_tables}"
