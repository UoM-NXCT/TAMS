"""Contains the database utility functions."""
from typing import Any


def dict_to_conn_str(config_dict: dict[str, dict[str, Any]]) -> str:
    """Return a Pyscopg connection string from a config dictionary.

    This is to turn the dictionary retrieved from the config TOML file to a string that
    the Pyscopg package can use to connect to the database.
    """
    config: dict[str, Any] = config_dict["postgresql"]
    host: str = config["host"]
    dbname: str = config["database"]
    user: str = config["user"]
    pwd: str = config["password"]
    conn_str: str = f"host={host} dbname={dbname} user={user} password={pwd}"
    return conn_str
