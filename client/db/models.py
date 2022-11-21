"""
Database class performs key database methods.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, Optional

from psycopg import Connection, Cursor, connect, errors


class Database:
    """The database model handles the database and its data."""

    def __init__(self, conn_str: str) -> None:
        """Initialise database connection class."""
        self.conn_str = conn_str
        self.conn: Connection[Any] | None = None  # The Psycopg connection
        self.cur: Cursor[Any] | None = None  # The connection cursor

    @staticmethod
    def attempt_sql_command(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorates sql commands with exception handling methods."""

        @wraps(func)
        def wrapper(self: Database, *args: Any, **kwargs: Any) -> None:
            """Attempt to execute the sql command, and handle any exceptions."""

            if self.conn:
                try:
                    func(self, *args, **kwargs)
                    self.conn.commit()
                except errors.DuplicateTable:
                    # Table already exists
                    logging.warning("Duplicate table. Performing rollback.")
                    self.conn.rollback()
            else:
                raise ConnectionError("Database connection is None")

        return wrapper

    @attempt_sql_command
    def exec(self, *args: Any, **kwargs: Any) -> None:
        """Attempt an SQL command."""

        if self.cur is not None and self.conn is not None:
            self.cur.execute(*args, **kwargs)
        else:
            logging.error("Connection does not exist.")

    def __enter__(self) -> Database:
        """The runtime context of the database class (connecting to the database)."""

        self.conn = connect(self.conn_str)
        self.cur = self.conn.cursor()

        # The 'with' statement binds the object to its 'as' clause (if specified).
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close the database connection upon exiting its runtime context."""
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def __repr__(self) -> str:
        """Return database version when class is repr() or str() is called."""

        if self.cur is not None:
            self.cur.execute("select version();")
            row: Optional[Any] = self.cur.fetchone()
            if not isinstance(row, tuple):
                raise TypeError("Pyscopg row is not a tuple. This is very bad!")
            return str(row[0])

        # If the cursor is None, the database is not connected.
        return str(None)


class DatabaseInitialiser(Database):
    """Initialise a database."""

    def __init__(self, conn_str: str) -> None:
        super().__init__(conn_str)

        self.base_dir: Path = Path(__file__).parent

    def init_db(self) -> None:
        """Create database tables."""

        logging.info("Creating database tables")

        init_instructions: Path = self.base_dir / "initialise.sql"

        with open(init_instructions, encoding="utf8") as sql_file:
            self.exec(sql_file.read())

    def populate_with_dummy_data(self) -> None:
        """
        Populate the tables with fake data. This should only be used in development.
        """

        logging.info("Populating database with fake data")

        dummy_data_instructions: Path = self.base_dir / "dummy_data.sql"
        with open(dummy_data_instructions, encoding="utf8") as sql_file:
            self.exec(sql_file.read())

    def __enter__(self) -> DatabaseInitialiser:
        """The runtime context of the database initialization class"""
        super().__enter__()
        return self


def init_database() -> None:
    """Initialize the database using initializer model."""

    # When running postgres via a container, localhost doesn't map to 127.0.0.1.
    conn_str: str = (
        "host=127.0.0.1 port=5432 dbname=tams user=postgres password=postgres"
    )

    with DatabaseInitialiser(conn_str) as db:
        db.init_db()
        db.populate_with_dummy_data()

    logging.info("Database initialised")
