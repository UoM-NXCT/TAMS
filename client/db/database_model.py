# -*- coding: utf-8 -*-
""" Database methods

This script contains the Database class which performs key database methods.

"""

import logging
from functools import wraps

from psycopg import Connection, Cursor, connect
from psycopg.errors import DuplicateTable


class Database:
    """The database model handles the database and its data."""

    def __init__(self, connection_string: str) -> None:
        """Initialise database connection class."""
        self.config = connection_string
        self.conn: Connection | None = None  # The Psycopg connection
        self.cur: Cursor | None = None  # The Pyscopg connection's cursor

    def __repr__(self) -> str:
        """Return database version when class is represented.

        NB absent __str__, str(self) fallbacks to __repr__!
        """

        if self.cur is not None:
            self.cur.execute("SELECT version()")
            db_version = str(self.cur.fetchone())
            return db_version
        return str(None)

    def __enter__(self):
        """The runtime context of the database class (connecting to the database)."""
        self.conn = connect(self.config)
        self.cur = self.conn.cursor()

        # The 'with' statement binds the object to its 'as' clause (if specified).
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the database connection upon exiting its runtime context."""
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    @staticmethod
    def attempt_sql_command(func):
        """Decorates sql commands with exception handling methods."""

        @wraps(func)
        def wrapper(self, *args, **kwargs) -> None:
            try:
                func(self, *args, **kwargs)
                self.conn.commit()
            except DuplicateTable:
                # Table already exists
                logging.exception("Exception raised. Performing rollback.")
                self.conn.rollback()

        return wrapper

    @attempt_sql_command
    def exec(self, *args, **kwargs) -> None:
        """Attempt an SQL command. Failing that, rollback."""
        if self.cur is not None and self.conn is not None:
            self.cur.execute(*args, **kwargs)
        else:
            logging.error("Connection does not exist!")
