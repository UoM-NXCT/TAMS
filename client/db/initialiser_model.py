"""Initialiser model

Contains a model that initialises the database. For use when first creating a database.
"""

import logging
from pathlib import Path

from client.db import Database


class DatabaseInitialiser(Database):
    """Initialise a database."""

    def init_db(self) -> None:
        """Create database tables."""

        logging.info("Creating database tables")

        init_instructions: Path = Path("initialise.sql")
        with open(init_instructions, encoding="utf8") as sql_file:
            self.exec(sql_file.read())

    def populate_with_dummy_data(self) -> None:
        """
        Populate the tables with fake data. This should only be used in development.
        """

        logging.info("Populating database with fake data")

        dummy_data_instructions: Path = Path("dummy_data.sql")
        with open(dummy_data_instructions, encoding="utf8") as sql_file:
            self.exec(sql_file.read())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # When running postgres via Docker, localhost doesn't map to 127.0.0.1; WTF??
    CONFIG = "host=127.0.0.1 port=5432 dbname=tams user=postgres password=postgres"
    with DatabaseInitialiser(CONFIG) as db:
        db.init_db()
        db.populate_with_dummy_data()
    logging.info("Database initialised")
