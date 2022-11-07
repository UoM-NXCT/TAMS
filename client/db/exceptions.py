"""
This file contains custom database exceptions.
"""


class MissingTables(Exception):
    """Exception raised upon missing tables."""

    def __init__(self, missing_tables: set[tuple], *args):
        super().__init__(*args)
        self.missing_tables: set[tuple] = missing_tables

    def __str__(self):
        return f"Database is missing the following tables: {self.missing_tables}"
