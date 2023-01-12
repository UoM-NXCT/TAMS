""" Archival script

This script archives data locally, in satellite storage, and in permanent storage.

It takes a directory of the form:

SEARCH_DIR/
├─ scan/
│  ├─ USER_FORM
│  ├─ scan reconstruction/

One scan may have many scan reconstructions.

This script looks in a given search directory and archives every scan it can find. By
default, it assumes that all directories in the search directory correspond to a scan
directory.

Each scan directory should have a user form file. This contains scan information input
by the user (for example, the scan name, project name, tomographer, et cetera). The
script uses this information to copy the data to the correct places:

SATELLITE/
├─ project_id/
│  ├─ scan_id/
│  │  ├─ scan_metadata
│  │  ├─ raw_data
│  │  ├─ ...
│  │  ├─ scan_reconstructions/
│  │  │  ├─ reconstruction_data

PERMANENT/
├─ project_id/
│  ├─ scan_id/
│  │  ├─ scan_metadata
│  │  ├─ raw_data
│  │  ├─ ...


This file can be imported as a module and contains the following functions:

    * get_cursor – get_cursor to SQL database
    * get_cursor – the get_cursor function of the script

"""


from pathlib import Path

from config import ini_file_params

from client.file_transfer.file_operations import (
    create_dir_if_missing,
    find_and_move,
    move_or_copy_item,
)

# Store path to directory that is searched for projects
SEARCH_DIR = Path(r"C:\test")
# Store path to directory to store all data (with reconstruction cf. SAT_STORAGE)
PERM_STORAGE_PATH = Path(r"C:\p")
# Store path to directory to store metadata_panel and raw data, but not reconstructions
SAT_STORAGE_PATH = Path(r"C:\s")
# Store name of user form file
USER_FORM_FILE = "_CTUSERFORM.ini"
# Store name of directories to be created
TRIUMVIRATE = ["_processing", "_tmp", "reconstructed data"]


if __name__ == "__main__":
    # Search through every directory in the search directory.
    # Assume each directory in the search directory is a scan directory.
    for scan_dir in (d for d in SEARCH_DIR.glob("*") if d.is_dir()):
        # Store project variables
        project_id = ""
        scan_id = ""

        # Search for user form file
        print(f"\nStage 1: accessing user form {USER_FORM_FILE} in {scan_dir}...")
        found = False
        for ini_file in scan_dir.glob(USER_FORM_FILE):
            if ini_file.name == USER_FORM_FILE:
                found = True
                print("User form file found. Reading...")
                try:
                    # Capture user form data from .ini file from info section
                    user_form = ini_file_params(ini_file, "info")
                    project_id = user_form["project_id"]
                    instrument_id = user_form["instrument_id"]
                    user_id = user_form["user_id"]
                    scan_id = user_form["scan_id"]
                    print(f"User form data: {user_form}")

                    # Create project directories in local storage and stat storage if
                    # they do not already exist
                    paths = [
                        PERM_STORAGE_PATH / project_id,
                        SAT_STORAGE_PATH / project_id,
                    ]
                    for path in paths:
                        create_dir_if_missing(path)
                except Exception as error:
                    print(error)
        if not found:
            print(f"Cannot find {USER_FORM_FILE}.")
            # Keep looking for directories with user form files in the search directory
            continue

        # Create a triumvirate in each scan directory (local, satellite, and permanent)
        print("\nStage 2: creating directories if they do not already exist...")
        base_dirs = {
            "local": scan_dir,
            "satellite": SAT_STORAGE_PATH / project_id / scan_id,
            "permanent": PERM_STORAGE_PATH / project_id / scan_id,
        }
        for dir_base in base_dirs.values():
            for dir_extension in TRIUMVIRATE:
                new_directory = Path(dir_base) / Path(dir_extension)
                create_dir_if_missing(new_directory)

        print(
            f"\nStage 3: find and move projections from {base_dirs['local']} to"
            " permanent and satellite storage directories."
        )
        find_and_move("*.tif", base_dirs["local"], [base_dirs["satellite"]], copy=True)
        find_and_move("*.tif", base_dirs["local"], [base_dirs["permanent"]], copy=True)

        print(
            "\nStage 4: find and move .xml, .xtekct, and .ANG files in"
            f" {base_dirs['local']} to satellite and permanent storage directories."
        )
        # Create list with the target destinations for the files
        destinations = [
            base_dirs["satellite"],
            base_dirs["permanent"],
        ]
        # Find and move .xml files
        find_and_move("*.xml", base_dirs["local"], destinations, copy=True)
        # Find and move .xtekct files
        find_and_move("*.xtekct", base_dirs["local"], destinations, copy=True)
        # Find and move .ANG files
        find_and_move("*.ang", base_dirs["local"], destinations, copy=True)

        # Find reconstructions and move to local reconstructed data directory
        print(
            "\nStage 5: find and move reconstructions to local reconstructed data"
            " directory."
        )
        local_reconstructed_data_directory = [base_dirs["local"] / "reconstructed data"]
        find_and_move(
            "*_01",
            base_dirs["local"],
            local_reconstructed_data_directory,
        )
        find_and_move(
            "*recon",
            base_dirs["local"],
            local_reconstructed_data_directory,
        )  # NOTE: This doesn't point to anything; intentional?

        # Find reconstructions and move to stat storage
        print(
            "\nStage 6: find and copy reconstructions to the stat reconstructed data"
            " directory."
        )
        for recon_dir in (
            d for d in (scan_dir / TRIUMVIRATE[2]).glob("*") if d.is_dir()
        ):
            move_or_copy_item(
                Path(recon_dir),
                base_dirs["satellite"] / TRIUMVIRATE[2],
            )

        # Find CentreSlices directory and move to stat and permanent storage
        print(
            "\nStage 7: find and move CentreSlices directory to satellite and permenant"
            " storage."
        )
        destinations = [
            base_dirs["satellite"],
            base_dirs["permanent"],
        ]
        find_and_move("*CentreSlice", Path(scan_dir), destinations)

    print("Done.")
