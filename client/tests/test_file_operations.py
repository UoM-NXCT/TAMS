import unittest
from pathlib import Path
from shutil import rmtree

from ..file_transfer.file_operations import (
    create_dir_if_missing,
    find_and_move,
    move_or_copy_item,
)


class TestFileOperations(unittest.TestCase):
    """Test functions in file_operations.py file."""

    def test_create_dir_if_missing(self) -> None:
        """Test function that creates a directory at a location if it doesn't exist."""
        dir_target = Path(r"client/tests/new_dir").absolute()
        self.assertEqual(False, dir_target.exists())
        create_dir_if_missing(dir_target)
        self.assertEqual(True, dir_target.exists())
        # Delete dir after test
        rmtree(dir_target)

    def test_move_item(self) -> None:
        """Test function that moves or copies an item."""

        # Test move functionality
        file_to_be_moved = Path(r"client/tests/text_files/move_me.txt").absolute()
        self.assertEqual(True, file_to_be_moved.is_file())
        target_dir_of_file_to_be_moved = Path(
            r"client/tests/example_directory"
        ).absolute()
        self.assertEqual(True, target_dir_of_file_to_be_moved.is_dir())
        move_or_copy_item(
            file_to_be_moved, target_dir_of_file_to_be_moved, keep_original=False
        )
        # File should no longer exist at original location, it should be at new location
        self.assertEqual(False, file_to_be_moved.is_file())
        location_of_moved_file = target_dir_of_file_to_be_moved / Path("move_me.txt")
        self.assertEqual(True, location_of_moved_file.is_file())
        # Move file back after test
        original_file_directory = Path(r"client/tests/text_files").absolute()
        move_or_copy_item(
            location_of_moved_file,
            original_file_directory,
            keep_original=False,
        )
        self.assertEqual(False, location_of_moved_file.is_file())

    def test_copy_item(self) -> None:
        """Test function that moves or copies an item."""

        # Test copy functionality
        file_to_be_copied = Path(r"client/tests/text_files/copy_me.txt").absolute()
        self.assertEqual(True, file_to_be_copied.is_file())
        target_dir_of_file_to_be_moved = Path(
            r"client/tests/example_directory"
        ).absolute()
        self.assertEqual(True, target_dir_of_file_to_be_moved.is_dir())
        move_or_copy_item(
            file_to_be_copied, target_dir_of_file_to_be_moved, keep_original=True
        )
        # File should exist at both locations
        self.assertEqual(True, file_to_be_copied.is_file())
        location_of_copied_file = target_dir_of_file_to_be_moved / Path("copy_me.txt")
        self.assertEqual(True, location_of_copied_file.is_file())
        # Delete file back after test
        location_of_copied_file.unlink()
        self.assertEqual(False, location_of_copied_file.is_file())

    def test_find_and_move(self) -> None:
        """Test function that finds and moves files from one directory to another."""

        source_dir = Path(r"client/tests/text_files").absolute()
        target_dir = Path(r"client/tests/example_directory").absolute()
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


if __name__ == "__main__":
    unittest.main()
