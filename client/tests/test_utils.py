"""Test utils module."""
import shutil
import unittest
from os import remove
from pathlib import Path
from shutil import rmtree

import pytest
import tomli_w

from client.utils.file import create_dir, find_and_move, move_item
from client.utils.hash import hash_in_chunks
from client.utils.toml import create_toml, load_toml, update_toml

TEST_DIR = Path(__file__).parent


class TestCreateDirectory(unittest.TestCase):
    """Test create_dir function."""

    def test_create_dir(self) -> None:
        """Test function that creates a directory at a location if it doesn't exist."""
        dir_target = TEST_DIR / Path("new_dir")
        assert not dir_target.exists()

        create_dir(dir_target)
        assert dir_target.exists()

        # Delete dir after test
        rmtree(dir_target)
        assert not dir_target.exists()

    def test_exc(self) -> None:
        """Test exception is raised if path is not a string or Path object."""
        with pytest.raises(TypeError):
            create_dir(1)  # type: ignore

        with pytest.raises(TypeError):
            create_dir(None)  # type: ignore


class TestMoveItem(unittest.TestCase):
    """Test the move_item function."""

    def test_move_item(self) -> None:
        """Test function that moves or copies an item."""
        # Check file exists
        file_to_be_moved = TEST_DIR / Path(r"text_files/move_me.txt")
        assert file_to_be_moved.is_file()

        # Check target directory exists
        target_dir_of_file_to_be_moved = TEST_DIR / Path("example_directory")
        assert target_dir_of_file_to_be_moved.is_dir()

        # Move file
        move_item(file_to_be_moved, target_dir_of_file_to_be_moved, keep_original=False)

        # File should no longer exist at original location, it should be at new location
        assert not file_to_be_moved.is_file()
        location_of_moved_file = target_dir_of_file_to_be_moved / Path("move_me.txt")
        assert location_of_moved_file.is_file()

        # Move file back after test
        original_file_dir = TEST_DIR / Path(r"text_files")
        move_item(
            location_of_moved_file,
            original_file_dir,
            keep_original=False,
        )
        assert not location_of_moved_file.is_file()
        assert file_to_be_moved.is_file()

    def test_move_dir(self) -> None:
        """Test function that moves or copies a directory."""
        # Check directory exists
        dir_to_be_moved = TEST_DIR / "text_files"
        member_of_dir_to_be_moved = dir_to_be_moved / "move_me.txt"
        assert dir_to_be_moved.is_dir()
        assert member_of_dir_to_be_moved.is_file()

        # Check target directory exists
        new_location = TEST_DIR / "example_directory"
        new_path = new_location / "text_files"
        moved_member_of_dir_to_be_moved = new_path / "move_me.txt"
        assert not new_path.is_dir()
        assert not moved_member_of_dir_to_be_moved.is_file()

        # Move directory
        move_item(dir_to_be_moved, new_location, keep_original=False)

        # Dir should no longer exist at original location, it should be at new location
        assert not dir_to_be_moved.is_dir()
        assert not member_of_dir_to_be_moved.is_file()
        assert new_path.is_dir()
        assert moved_member_of_dir_to_be_moved.is_file()

        # Move directory back after test
        move_item(
            new_path,
            TEST_DIR,
            keep_original=False,
        )
        assert not new_path.is_dir()
        assert not moved_member_of_dir_to_be_moved.is_file()
        assert dir_to_be_moved.is_dir()
        assert member_of_dir_to_be_moved.is_file()

    def test_copy_item(self) -> None:
        """Test function that moves or copies an item."""
        # Check file exists
        file_to_be_copied = TEST_DIR / Path("text_files/copy_me.txt")
        assert file_to_be_copied.is_file()

        # Check target directory exists
        target_dir_of_file_to_be_moved = TEST_DIR / Path("example_directory")
        assert target_dir_of_file_to_be_moved.is_dir()

        # Copy file
        move_item(file_to_be_copied, target_dir_of_file_to_be_moved, keep_original=True)

        # File should exist at both locations
        assert file_to_be_copied.is_file()
        location_of_copied_file = target_dir_of_file_to_be_moved / Path("copy_me.txt")
        assert location_of_copied_file.is_file()

        # Delete file back after test
        location_of_copied_file.unlink()
        assert not location_of_copied_file.is_file()

    def test_copy_dir(self) -> None:
        """Test function that moves or copies a directory."""
        # Check directory exists
        dir_to_be_moved = TEST_DIR / "text_files"
        member_of_dir_to_be_moved = dir_to_be_moved / "move_me.txt"
        assert dir_to_be_moved.is_dir()
        assert member_of_dir_to_be_moved.is_file()

        # Check target directory does not exist
        new_location = TEST_DIR / "example_directory"
        new_path = new_location / "text_files"
        moved_member_of_dir_to_be_moved = new_path / "move_me.txt"
        assert not new_path.is_dir()
        assert not moved_member_of_dir_to_be_moved.is_file()

        # Move directory
        move_item(dir_to_be_moved, new_location, keep_original=True)

        # Director should exist at both locations
        assert dir_to_be_moved.is_dir()
        assert member_of_dir_to_be_moved.is_file()
        assert new_path.is_dir()
        assert moved_member_of_dir_to_be_moved.is_file()

        # Delete directory back after test
        shutil.rmtree(new_path)
        assert not new_path.is_dir()
        assert not moved_member_of_dir_to_be_moved.is_file()
        assert dir_to_be_moved.is_dir()
        assert member_of_dir_to_be_moved.is_file()


class TestFile(unittest.TestCase):
    """Test functions in file.py utils file."""

    def test_find_and_move(self) -> None:
        """Test function that finds and moves files from one directory to another."""
        source_dir = TEST_DIR / Path(r"text_files")
        target_dir = TEST_DIR / Path(r"example_directory")

        find_and_move("*.txt", source_dir, target_dir)

        copy_me_text_file_init = source_dir / Path("copy_me.txt")
        move_me_text_file_init = source_dir / Path("move_me.txt")
        copy_me_text_file_final = target_dir / Path("copy_me.txt")
        move_me_text_file_final = target_dir / Path("move_me.txt")

        assert False is copy_me_text_file_init.is_file()
        assert True is copy_me_text_file_final.is_file()
        assert False is move_me_text_file_init.is_file()
        assert True is move_me_text_file_final.is_file()

        # Move files back after test
        find_and_move("*.txt", target_dir, source_dir)


class TestTOML(unittest.TestCase):
    """Test functions in toml.py utils file."""

    def test_create_toml(self) -> None:
        """Test function that creates TOML file with given data."""
        new_toml_path = TEST_DIR / Path("new_toml.toml")
        dict_to_be_stored = {"Scientist": {"name": "Einstein", "thesis_year": 1905}}
        create_toml(new_toml_path, dict_to_be_stored)
        assert True is new_toml_path.is_file()
        assert new_toml_path.name == "new_toml.toml"
        stored_dict = load_toml(new_toml_path)
        assert dict_to_be_stored == stored_dict

        # Delete the created TOML file after tests have been completed
        remove(new_toml_path)

    def test_get_dict_from_toml(self) -> None:
        """Test function that returns a dictionary from a TOML file."""
        path_to_toml = TEST_DIR / Path("test_toml_files/my_cat.toml")
        toml_dict = load_toml(path_to_toml)
        expected_dict = {"cat": {"name": "Dusty", "age": 7}}
        assert expected_dict == toml_dict

    def test_update_toml(self) -> None:
        """Test a function that updates a TOML file with given data."""
        path_to_toml = TEST_DIR / Path("test_toml_files/my_dog.toml")
        update_toml(path_to_toml, "dog", "age", 12)
        new_age = load_toml(path_to_toml)["dog"]["age"]
        assert new_age == 12
        update_toml(path_to_toml, "dog", "is_cute", True)
        cute = load_toml(path_to_toml)["dog"]["is_cute"]
        assert True is cute

        # Now reset the TOML file for future testing
        with open(path_to_toml, mode="wb") as file:
            data = {"dog": {"name": "Loca", "age": 10}}
            tomli_w.dump(data, file)


class TestHash(unittest.TestCase):
    def test_hash_in_chunks(self):
        """Test function that hashes a file in chunks."""
        file_to_hash: Path = TEST_DIR / Path("text_files/copy_me.txt")
        hash_value: str = hash_in_chunks(file_to_hash)
        self.assertEqual(
            "47d7f25678e02dd969b7699a2f0309128bc2dbc6c09daa64c135cf9af7630883511a073db91c10c4694846db8c77d63d",  # noqa
            hash_value,
        )
