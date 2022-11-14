"""Contains the database utility functions."""

from typing import Any


def dict_to_conn_str(config_dict: dict[str, dict[str, Any]]) -> str:
    """Return a Pyscopg connection string from a config dictionary.

    This is to turn the dictionary retrieved from the config TOML file to a string that
    the Pyscopg package can use to connect to the database.
    """
    psql_config: dict[str, Any] = config_dict["postgresql"]
    host: str = psql_config["host"]
    dbname: str = psql_config["database"]
    user: str = psql_config["user"]
    password: str = psql_config["password"]
    conn_str: str = f"host={host} dbname={dbname} user={user} password" f"={password}"
    return conn_str
