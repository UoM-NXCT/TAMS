# -*- coding: utf-8 -*-
""" Database views

This files classes to represent data from the database to the user.
"""

import logging
from typing import Any

from .database_model import Database
from .exceptions import MissingTables


class DatabaseView:
    """Represent data from the database."""

    def __init__(self, connection_string: str) -> None:
        """Initialise database view and connect to database."""

        self.connection_string = connection_string
        with Database(self.connection_string) as database:
            if database.conn.closed:
                raise ConnectionError("Unable to connect to database")
            logging.info("Connection to database in DatabaseView successful.")

    def get_tables(self) -> list[tuple]:
        """Get list of tables in database."""

        query = "select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE';"
        with Database(self.connection_string) as database:
            database.exec(query)
            return database.cur.fetchall()

    def validate_tables(self) -> None:
        """Validate tables in database; raises an exception if they are not valid."""

        # Check the required tables exist
        tables_needed: set[tuple] = {
            ("project",),
        }
        tables_present: set[tuple] = set(self.get_tables())
        missing_tables: set[tuple] = tables_needed - tables_present
        if missing_tables:
            raise MissingTables(missing_tables)

    def view_select_from_where(
        self, select_value: str, from_value: str, *where_value: tuple[str] | str
    ) -> tuple[list[tuple], list[str]]:
        """Return selection."""

        # Construct SQL query
        query = f"select {select_value} from {from_value}"
        if where_value:
            # Get rid of trailing comma in tuple
            where_value_formatted: str = ",".join([str(x) for x in where_value])
            query = f"{query} where {where_value_formatted}"
        query = f"{query};"

        # Get data
        with Database(self.connection_string) as database:
            database.exec(query)
            data = database.cur.fetchall()
        if select_value == "*":
            # TODO: Deal with wildcard select.
            column_headers = ["TBD"]
        else:
            column_headers = list(select_value.replace(" ", "").split(","))
            print(column_headers)

        return data, column_headers

    def get_version(self) -> str:
        """Get database version."""

        query = "select version();"
        with Database(self.connection_string) as database:
            database.exec(query)
            version = str(database.cur.fetchone())
        return version

    def get_project_metadata(self, project_id: int) -> tuple[tuple[Any], list[str]]:
        """Get project title, type, summary, keywords, dates, and directory."""
        data, column_headers = self.view_select_from_where(
            "title, project_type, summary, keyword",
            "project",
            f"project_id={project_id}",
        )
        return data[0], column_headers
