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
    else:
        raise TypeError("Path must be a string or a Path object.")

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

    item_dest: Path = dest_dir / item.name

    try:

        # Check file or directory is a file or directory, respectively
        if item.is_file():
            shutil.copy(item, item_dest)
        elif item.is_dir():
            shutil.copytree(item, item_dest)

        # Delete original if not keeping original
        if not keep_original:
            if item.is_file():
                os.remove(item)
            elif item.is_dir():
                os.rmdir(item)

    except FileExistsError:
        # Just move on if the file already exists
        logging.info("File already exists at %s, skipping", item_dest)


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

    num_of_items = len(tuple(search_dir.glob(glob_arg)))
    if num_of_items:
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

    for unit in ("B", "KB", "MB", "TB", "PB"):
        if num_of_bytes < 1024 or unit == "PB":
            return f"{num_of_bytes:.{dec_places}f} {unit}"
        num_of_bytes /= 1024
    raise RuntimeError("Size format failed. Number of bytes too large?")
