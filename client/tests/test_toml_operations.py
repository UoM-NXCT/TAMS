# -*- coding: utf-8 -*-
import unittest
from os import remove
from pathlib import Path

import tomli_w

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from client.settings.toml_operations import (
    create_toml,
    get_dict_from_toml,
    get_value_from_toml,
    update_toml,
)


class TestTOML(unittest.TestCase):
    """Test functions in toml_operations.py file."""

    def test_create_toml(self) -> None:
        """Test function that creates TOML file with given data."""

        new_toml_path = Path(r"client/tests/new_toml.toml")
        dict_to_be_stored = {"Scientist": {"name": "Einstein", "thesis_year": 1905}}
        create_toml(new_toml_path, dict_to_be_stored)
        self.assertEqual(True, new_toml_path.is_file())
        self.assertEqual("new_toml.toml", new_toml_path.name)
        stored_dict = get_dict_from_toml(new_toml_path)
        self.assertEqual(dict_to_be_stored, stored_dict)

        # Delete the created TOML file after tests have been completed
        remove(new_toml_path)

    def test_get_dict_from_toml(self) -> None:
        """Test function that returns a dictionary from a TOML file."""

        path_to_toml = Path(r"client/tests/test_toml_files/my_cat.toml")
        toml_dict = get_dict_from_toml(path_to_toml)
        expected_dict = {"cat": {"name": "Dusty", "age": 7}}
        self.assertEqual(toml_dict, expected_dict)

    def test_get_value_from_toml(self) -> None:
        """Test a function that returns a value from a TOML file."""

        path_to_toml = Path(r"client/tests/test_toml_files/my_cat.toml")
        cat_name = get_value_from_toml(path_to_toml, "cat", "name")
        cat_age = get_value_from_toml(path_to_toml, "cat", "age")
        self.assertEqual(cat_name, "Dusty")
        self.assertEqual(cat_age, 7)

    def test_update_toml(self) -> None:
        """Test a function that updates a TOML file with given data."""

        path_to_toml = Path(r"client/tests/test_toml_files/my_dog.toml")
        update_toml(path_to_toml, "dog", "age", 12)
        new_age = get_value_from_toml(path_to_toml, "dog", "age")
        self.assertEqual(12, new_age)
        update_toml(path_to_toml, "dog", "is_cute", True)
        cute = get_value_from_toml(path_to_toml, "dog", "is_cute")
        self.assertEqual(True, cute)

        # Now reset the TOML file for future testing
        with open(path_to_toml, mode="wb") as file:
            data = {"dog": {"name": "Loca", "age": 10}}
            tomli_w.dump(data, file)


if __name__ == "__main__":
    unittest.main()
