"""
Evaluate run-time constants.
"""
import logging
from importlib import metadata

# Get the version of the package
try:
    __version__ = metadata.version("Tomography Archival Management System")
except metadata.PackageNotFoundError:
    logging.exception(
        "Could not find package metadata during init. Setting version to 'unknown'."
    )
    __version__ = "unknown"
