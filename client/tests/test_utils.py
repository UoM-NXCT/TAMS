"""
Test utils module.
"""

import unittest
from os import remove
from pathlib import Path
from shutil import rmtree

import tomli_w

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from client.utils.file import create_dir_if_missing, find_and_move, move_item
from client.utils.toml import (
    create_toml,
    get_dict_from_toml,
    get_value_from_toml,
    update_toml,
)

TEST_DIR = Path(__file__).parent


class TestFile(unittest.TestCase):
    """Test functions in file.py utils file."""

    def test_create_dir_if_missing(self) -> None:
        """Test function that creates a directory at a location if it doesn't exist."""
        dir_target = TEST_DIR / Path("new_dir")
        self.assertEqual(False, dir_target.exists())
        create_dir_if_missing(dir_target)
        self.assertEqual(True, dir_target.exists())
        # Delete dir after test
        rmtree(dir_target)

    def test_move_item(self) -> None:
        """Test function that moves or copies an item."""

        # Test move functionality
        file_to_be_moved = TEST_DIR / Path(r"text_files/move_me.txt")
        self.assertEqual(True, file_to_be_moved.is_file())
        target_dir_of_file_to_be_moved = TEST_DIR / Path("example_directory")
        self.assertEqual(True, target_dir_of_file_to_be_moved.is_dir())
        move_item(file_to_be_moved, target_dir_of_file_to_be_moved, keep_original=False)
        # File should no longer exist at original location, it should be at new location
        self.assertEqual(False, file_to_be_moved.is_file())
        location_of_moved_file = target_dir_of_file_to_be_moved / Path("move_me.txt")
        self.assertEqual(True, location_of_moved_file.is_file())
        # Move file back after test
        original_file_directory = TEST_DIR / Path(r"text_files")
        move_item(
            location_of_moved_file,
            original_file_directory,
            keep_original=False,
        )
        self.assertEqual(False, location_of_moved_file.is_file())

    def test_copy_item(self) -> None:
        """Test function that moves or copies an item."""

        # Test copy functionality
        file_to_be_copied = TEST_DIR / Path("text_files/copy_me.txt")
        self.assertEqual(True, file_to_be_copied.is_file())
        target_dir_of_file_to_be_moved = TEST_DIR / Path("example_directory")
        self.assertEqual(True, target_dir_of_file_to_be_moved.is_dir())
        move_item(file_to_be_copied, target_dir_of_file_to_be_moved, keep_original=True)

        # File should exist at both locations
        self.assertEqual(True, file_to_be_copied.is_file())
        location_of_copied_file = target_dir_of_file_to_be_moved / Path("copy_me.txt")
        self.assertEqual(True, location_of_copied_file.is_file())

        # Delete file back after test
        location_of_copied_file.unlink()
        self.assertEqual(False, location_of_copied_file.is_file())

    def test_find_and_move(self) -> None:
        """Test function that finds and moves files from one directory to another."""

        source_dir = TEST_DIR / Path(r"text_files")
        target_dir = TEST_DIR / Path(r"example_directory")

        find_and_move("*.txt", source_dir, target_dir)

        copy_me_text_file_init = source_dir / Path("copy_me.txt")
        move_me_text_file_init = source_dir / Path("move_me.txt")
        copy_me_text_file_final = target_dir / Path("copy_me.txt")
        move_me_text_file_final = target_dir / Path("move_me.txt")

        self.assertEqual(False, copy_me_text_file_init.is_file())
        self.assertEqual(True, copy_me_text_file_final.is_file())
        self.assertEqual(False, move_me_text_file_init.is_file())
        self.assertEqual(True, move_me_text_file_final.is_file())

        # Move files back after test
        find_and_move("*.txt", target_dir, source_dir)


class TestTOML(unittest.TestCase):
    """Test functions in toml.py utils file."""

    def test_create_toml(self) -> None:
        """Test function that creates TOML file with given data."""

        new_toml_path = TEST_DIR / Path("new_toml.toml")
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

        path_to_toml = TEST_DIR / Path("test_toml_files/my_cat.toml")
        toml_dict = get_dict_from_toml(path_to_toml)
        expected_dict = {"cat": {"name": "Dusty", "age": 7}}
        self.assertEqual(expected_dict, toml_dict)

    def test_get_value_from_toml(self) -> None:
        """Test a function that returns a value from a TOML file."""

        path_to_toml = TEST_DIR / Path("test_toml_files/my_cat.toml")
        cat_name = get_value_from_toml(path_to_toml, "cat", "name")
        cat_age = get_value_from_toml(path_to_toml, "cat", "age")
        self.assertEqual(cat_name, "Dusty")
        self.assertEqual(cat_age, 7)

    def test_update_toml(self) -> None:
        """Test a function that updates a TOML file with given data."""

        path_to_toml = TEST_DIR / Path("test_toml_files/my_dog.toml")
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
