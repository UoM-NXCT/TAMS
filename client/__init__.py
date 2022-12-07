"""
Evaluate run-time constants.
"""
from importlib import metadata

from client.utils import log

# Get the version of the package
try:
    # FIXME: This doesn't seem to work and raises an exception (see below).
    __version__ = metadata.version(__name__)
except metadata.PackageNotFoundError:
    log.logger(__name__).error(
        "Could not find %s metadata during init. Setting version to 'unknown'.",
        __name__,
    )
    __version__ = "unknown"
