"""
Handle the thumbnail image for the metadata panel.
"""

import logging
from pathlib import Path

from client import settings
from client.utils.toml import get_value_from_toml


def get_thumbnail(project_id: int, scan_id: int | None = None) -> Path:
    """Return the first image in the scan directory as a thumbnail."""

    # Get the path to the local library directory
    local_library: Path = Path(
        get_value_from_toml(settings.general, "storage", "local_library")
    )

    scan_dir: Path
    if scan_id:
        # Get the path to the local scan directory
        scan_dir = local_library / str(project_id) / str(scan_id)
    else:
        # If no scan ID is provided, get the path to the local project directory
        scan_dir = local_library / str(project_id)

    # List of file extensions to search for; order matters!
    image_extensions: tuple[str, ...] = (
        "tiff",
        "tif",
        "bmp",
        "jpg",
        "jpeg",
        "png",
        "gif",
    )

    # Search recursively for the first image in the scan directory
    for extension in image_extensions:
        images: tuple[Path, ...] = tuple(scan_dir.rglob(f"*.{extension}"))
        if images:
            return images[0]

    # If no images are found, return the placeholder image
    logging.warning("No images found in %s", scan_dir)
    return settings.placeholder_image
