"""
Common file operation methods.
"""

import logging
import os
import shutil
from pathlib import Path


def create_dir(path: Path | str) -> None:
    """Create a directory if one does not exist.

    :param path: target directory
    """

    # If directory exists, do nothing
    if isinstance(path, Path):
        if path.exists():
            return
    elif isinstance(path, str):
        if os.path.exists(path):
            return

    # Create directory
    os.makedirs(path, exist_ok=True)
    logging.info("Created directory at %s", path)


def move_item(item: Path, dest_dir: Path, keep_original: bool = True) -> None:
    """Function that copies or moves item to a given location.

    :param item: target item (file or directory)
    :param dest_dir: destination location
    :param keep_original: determines if move or copy
    """

    # Create destination directory if it does not exist
    create_dir(dest_dir)

    try:

        # Check file or directory is a file or directory, respectively
        if item.is_file():
            shutil.copy(item, dest_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, dest_dir / item.name)

        # Delete original if not keeping original
        if not keep_original:
            if item.is_file():
                os.remove(item)
            elif item.is_dir():
                os.rmdir(item)

    # If source and destination are same
    except shutil.SameFileError:
        logging.exception("Exception raised.")
    # If any permission issue
    except PermissionError:
        logging.exception("Exception raised.")
    except FileExistsError:
        # Just move on if the file already exists
        logging.info("File already exists at %s, skipping", dest_dir / item.name)


def find_and_move(
    glob_arg: str,
    search_dir: Path,
    *destinations: Path,
    copy: bool = False,
) -> None:
    """Function that finds files using .glob method in given directory and moves them to
    another directory.

    :param copy: doesn't delete original if true
    :param glob_arg: argument passed to .glob method
    :param search_dir: directory that is searched
    :param destinations: list of destinations
    """

    number_of_counters = len(tuple(search_dir.glob(glob_arg)))
    if number_of_counters:
        for dest in destinations:
            for item in tuple(search_dir.glob(glob_arg)):
                # Copy file to local reconstructed data directory
                move_item(
                    item,
                    Path(search_dir) / Path(dest),
                )

        if not copy:
            for item in tuple(search_dir.glob(glob_arg)):
                if item.is_file():
                    os.remove(item)
                elif item.is_dir():
                    shutil.rmtree(item)
    else:
        logging.warning("No %s files found.", glob_arg)


def size_fmt(num_of_bytes: int | float, dec_places: int = 2) -> str:
    """Function that formats a size in bytes to a human-readable format."""

    if num_of_bytes < 0:
        raise ValueError("Number of bytes must be positive.")

    selected_unit: str = "Err"
    for unit in ("B", "KB", "MB", "TB", "PB"):
        if num_of_bytes < 1024 or unit == "PB":
            selected_unit = unit
            break
        num_of_bytes /= 1024
    return f"{num_of_bytes:.{dec_places}f} {selected_unit}"
