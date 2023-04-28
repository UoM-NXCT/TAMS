"""Database class performs key database methods."""

from __future__ import annotations

import logging
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any

from psycopg import connect, errors

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType


class Database:
    """The database model handles the database and its data."""

    def __init__(self: Database, conn_str: str) -> None:
        """Initialise database connection class."""
        self.conn_str = conn_str
        self.conn = None  # Psycopg connection
        self.cur = None  # Connection cursor

    @staticmethod
    def attempt_sql_command(func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorate SQL commands with exception handling methods."""

        @wraps(func)
        def wrapper(
            self: Database, *args: tuple[Any, ...], **kwargs: dict[str, Any]
        ) -> None:
            """Attempt to execute the sql command, and handle any exceptions."""
            if self.conn:
                try:
                    func(self, *args, **kwargs)
                    self.conn.commit()
                except errors.DuplicateTable:
                    logging.warning("Duplicate table. Performing rollback.")
                    self.conn.rollback()
            else:
                msg = "Connection does not exist."
                raise ConnectionError(msg)

        return wrapper

    @attempt_sql_command
    def exec_sql(
        self: Database, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        """Attempt an SQL command."""
        if self.cur is not None and self.conn is not None:
            self.cur.execute(*args, **kwargs)
        else:
            logging.error("Connection does not exist.")

    def __enter__(self: Database) -> Database:
        """Runtime context of the database class (connecting to the database)."""
        self.conn = connect(self.conn_str)
        self.cur = self.conn.cursor()
        return self  # Bind to 'as' clause in 'with' statement

    def __exit__(
        self: Database,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        """Close the database connection upon exiting its runtime context."""
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def __repr__(self: Database) -> str:
        """Return database version when class is repr() or str() is called."""
        if self.cur is not None:
            self.cur.execute("select version();")
            row = self.cur.fetchone()
            return str(row[0])
        return str(None)


class DatabaseInitializer(Database):
    """Initialise a database."""

    def __init__(self: DatabaseInitializer, conn_str: str) -> None:
        """Initialise the database initializer."""
        super().__init__(conn_str)
        self.base_dir = Path(__file__).parent

    def init_db(self: DatabaseInitializer) -> None:
        """Create database tables."""
        logging.info("Creating database tables")
        init_instructions = self.base_dir / "initialise.sql"
        with open(init_instructions, encoding="utf8") as sql_file:
            self.exec_sql(sql_file.read())

    def populate_with_dummy_data(self: DatabaseInitializer) -> None:
        """Populate the tables with fake data.

        This should only be used in development.
        """
        logging.info("Populating database with fake data")
        dummy_data_instructions = self.base_dir / "dummy_data.sql"
        with open(dummy_data_instructions, encoding="utf8") as sql_file:
            self.exec_sql(sql_file.read())


def init_database() -> None:
    """Initialize the database using initializer model."""
    # When running postgres via a container, localhost doesn't map to 127.0.0.1.
    conn_str = "host=127.0.0.1 port=5432 dbname=tams user=postgres password=postgres"
    with DatabaseInitializer(conn_str) as db:
        db.init_db()
        db.populate_with_dummy_data()
    logging.info("Database initialised")
