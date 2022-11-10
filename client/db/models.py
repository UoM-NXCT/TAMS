"""
Database class performs key database methods.
"""

import logging
from functools import wraps
from pathlib import Path

from psycopg import Connection, Cursor, connect, errors


class Database:
    """The database model handles the database and its data."""

    def __init__(self, conn_str: str) -> None:
        """Initialise database connection class."""
        self.conn_str = conn_str
        self.conn: Connection | None = None  # The Psycopg connection
        self.cur: Cursor | None = None  # The connection cursor

    def __repr__(self) -> str:
        """Return database version when class is repr() or str() is called."""

        if self.cur is not None:
            self.cur.execute("select version();")
            row: tuple[str, ...] = self.cur.fetchone()
            return row[0]  # mypy complains but this is correct

        # If the cursor is None, the database is not connected.
        return str(None)

    def __enter__(self):
        """The runtime context of the database class (connecting to the database)."""

        self.conn = connect(self.conn_str)
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
            except errors.DuplicateTable:
                # Table already exists
                logging.warning("Duplicate table. Performing rollback.")
                self.conn.rollback()

        return wrapper

    @attempt_sql_command
    def exec(self, *args, **kwargs) -> None:
        """Attempt an SQL command."""

        if self.cur is not None and self.conn is not None:
            self.cur.execute(*args, **kwargs)
        else:
            logging.error("Connection does not exist.")


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
