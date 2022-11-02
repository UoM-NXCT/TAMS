# -*- coding: utf-8 -*-
""" File operation methods

This script contains common file operation methods.

This script requires that `tqdm` be installed within the Python environment you are
running this script in.

This file can be imported as a module and contains the following
functions:

    * create_if_missing - creates a directory if one does not exist
    * move_or_copy_item - moves or copies item
    * find_and_move - finds files in a given directory and moves them

"""

import logging
import os
import shutil
from pathlib import Path

from tqdm import tqdm


def create_dir_if_missing(path: Path) -> None:
    """Function that creates a directory if one does not exist.

    :param path: target directory
    :return:
    """
    if not path.exists():
        os.makedirs(path, exist_ok=True)
        logging.info("Created directory at %s.", path)
    elif path.exists():
        logging.info("Did not create directory at %s as it already exists.", path)


def move_or_copy_item(
    item: Path, destination_directory: Path, keep_original: bool = True
) -> None:
    """Function that copies or moves item to a given location.

    :param item: target item
    :param destination_directory: destination location
    :param keep_original: determines if move or copy
    """
    if keep_original:
        verb = "Copying"
    else:
        verb = "Moving"
    logging.info("%s %s to %s...", verb, item, destination_directory)
    create_dir_if_missing(destination_directory)
    try:
        if item.is_file():
            shutil.copy(item, destination_directory / item.name)
        elif item.is_dir():
            shutil.copytree(item, destination_directory / item.name)
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


def find_and_move(
    glob_arg: str, search_dir: Path, *destinations: Path, copy: bool = False
) -> None:
    """Function that finds files using .glob method in given directory and moves them to
    another directory.

    :param copy: doesn't delete original if true
    :param glob_arg: argument passed to .glob method
    :param search_dir: directory that is searched
    :param destinations: list of destinations
    """
    number_of_counters = len(list(search_dir.glob(glob_arg)))
    if number_of_counters:
        for destination in destinations:
            for item in tqdm(
                search_dir.glob(glob_arg),
                f"Moving {glob_arg} files from {search_dir} to {destination}",
                total=len(list(search_dir.glob(glob_arg))),
            ):
                # Copy file to local reconstructed data directory
                move_or_copy_item(
                    item,
                    Path(search_dir) / Path(destination),
                )
        for item in tqdm(
            search_dir.glob(glob_arg),
            f"Deleting {glob_arg} files from {search_dir}",
            total=len(list(search_dir.glob(glob_arg))),
        ):
            if not copy:
                if item.is_file():
                    os.remove(item)
                elif item.is_dir():
                    shutil.rmtree(item)
    else:
        logging.warning("No %s files found.", glob_arg)
