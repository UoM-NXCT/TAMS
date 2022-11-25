"""
Handle the thumbnail image for the metadata panel.
"""

from pathlib import Path

from client import settings


def get_thumbnail(prj_id: int, scan_id: int | None = None) -> Path:
    """Return the first image in the scan directory as a thumbnail."""

    # Get the path to the local library directory
    local_lib: Path = Path(settings.get_lib("local"))

    scan_dir: Path
    if scan_id:
        # Get the path to the local scan directory
        scan_dir = local_lib / str(prj_id) / str(scan_id)
    else:
        # If no scan ID is provided, get the path to the local project directory
        scan_dir = local_lib / str(prj_id)

    # List of file extensions to search for; order matters!
    extensions: tuple[str, ...] = (
        "tiff",
        "tif",
        "bmp",
        "jpg",
        "jpeg",
        "png",
        "gif",
    )

    # Search recursively for the first image in the scan directory
    for ext in extensions:
        images: tuple[Path, ...] = tuple(scan_dir.rglob(f"*.{ext}"))
        if images:
            return images[0]

    # If no images are found, return the placeholder image
    return settings.placeholder_image
