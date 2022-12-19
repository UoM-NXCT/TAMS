"""
Common TOML file operation methods.
"""

import tomllib
from pathlib import Path
from typing import Any

import tomli_w


def create_toml(path: Path | str, data: dict[str, Any]) -> None:
    """Create a new TOML file with given data

    :param path: path to new TOML file
    :param data: data to be stored in TOML file as a dictionary
    """

    with open(path, mode="wb") as f:
        tomli_w.dump(data, f)


def update_toml(path: Path | str, section: str, key: str, value: object) -> None:
    """Update or add a value in a given TOML using a section and key index.

    :param path: target TOML file
    :param section: the section of the TOML file that contains the target value
    :param key: the key corresponding to the target value
    :param value: the value to be added or updated
    """

    with open(path, mode="rb") as f:
        # Load the TOML file as a dictionary
        data: dict[str, Any] = tomllib.load(f)
        if key in data[section]:
            # If key exists, update value
            data[section][key] = value
        else:
            # If key does not exist, add key and value
            data[section].update({key: value})

    # Write the updated dictionary to the TOML file
    with open(path, mode="wb") as f:
        tomli_w.dump(data, f)


def load_toml(path: Path) -> dict[str, Any]:
    """Return the data from a TOML file as a Python dictionary.

    :param path: target TOML file
    """

    with open(path, mode="rb") as f:
        data: dict[str, Any] = tomllib.load(f)
        return data
