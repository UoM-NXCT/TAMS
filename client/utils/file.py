"""Common file operation methods."""

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
        msg = "Path must be a string or a Path object."
        raise TypeError(msg)

    # Create directory
    os.makedirs(path, exist_ok=True)
    logging.info("Created directory at %s", path)


def move_item(item: Path, dest_dir: Path, keep_original: bool = True) -> None:
    """Copy or move item to a given location.

    :param item: target item (file or directory)
    :param dest_dir: destination location
    :param keep_original: determines if move or copy
    """
    # Create destination directory if it does not exist
    create_dir(dest_dir)

    item_dest: Path = dest_dir / item.name
    try:
        if item.is_file():
            logging.info("Copying file %s to %s", item, item_dest)
            shutil.copy(item, item_dest)
        else:
            logging.info("Copying directory %s to %s", item, item_dest)
            shutil.copytree(item, item_dest)
    except FileExistsError:
        logging.info("File already exists at %s, skipping", item_dest)
    except FileNotFoundError:
        logging.warning("File not found at %s", item)
        raise
    else:
        if not keep_original:
            if item.is_file():
                os.remove(item)
            else:
                shutil.rmtree(item)


def find_and_move(
    glob_arg: str,
    search_dir: Path,
    *destinations: Path,
    copy: bool = False,
) -> None:
    """Find files in given directory and moves them to another directory.

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
    """Format a size in bytes to a human-readable format."""
    if num_of_bytes < 0:
        msg = f"Number of bytes must be positive, not {num_of_bytes}."
        raise ValueError(msg)
    divisor = 1024
    for unit in ("B", "KB", "MB", "TB", "PB"):
        if num_of_bytes < divisor or unit == "PB":
            return f"{num_of_bytes:.{dec_places}f} {unit}"
        num_of_bytes /= divisor
    msg = "Number of bytes must be less than 1024 PB."
    raise RuntimeError(msg)
