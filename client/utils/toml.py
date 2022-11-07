"""
Common TOML file operation methods.
"""

import logging
from pathlib import Path
from typing import Any

# As of Python 3.11, tomllib is the preferred way of reading TOML files.
# We should attempt to import it, but use tomli if tomllib fails to import.
try:
    import tomllib  # noqa
except ModuleNotFoundError:
    import tomli as tomllib

import tomli_w


def create_toml(toml_file: Path, config: dict) -> None:
    """Create a new TOML file with given config data

    :param toml_file: path to new TOML file
    :param config: data to be stored in TOML file
    """

    with open(toml_file, mode="wb") as file:
        tomli_w.dump(config, file)


def update_toml(toml_file: Path, section: str, key: str, value: object) -> None:
    """Update or add a value in a given TOML using a section and key index.

    :param toml_file: target TOML file
    :param section: the section of the TOML file that contains the target value
    :param key: the key corresponding to the target value
    :param value: the value to be added or updated
    """

    with open(toml_file, mode="rb") as file:
        config: dict[str, Any] = tomllib.load(file)
        if key in config[section]:
            config[section][key] = value
        else:
            config[section].update({key: value})
        file.close()
    with open(toml_file, mode="wb") as file:
        tomli_w.dump(config, file)


def get_dict_from_toml(toml_file: Path) -> dict | None:
    """Return the data from a TOML file as a Python dictionary.

    :param toml_file: target TOML file
    :return: a Python dictionary of the date from the TOML file or None if the method
    encounters an exception
    """

    try:
        with open(toml_file, mode="rb") as file:
            config: dict[str, Any] = tomllib.load(file)
            return config
    except FileNotFoundError:
        logging.exception("Exception occurred")
    return None


def get_value_from_toml(toml_file: Path, section: str, key: str) -> Any:
    """Return the value from a given key in a section of a given TOML file.

    :param toml_file: target TOML file
    :param section: target section
    :param key: target key
    :return: the value from the TOML file or None if the method encounters an exception
    """

    with open(toml_file, mode="rb") as file:
        config: dict[str, Any] = tomllib.load(file)
        value: Any = config[section][key]
        return value
