"""
File hashing algorithms.
"""
from __future__ import annotations

from hashlib import sha3_384
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def hash_in_chunks(file: Path | str) -> str:
    """Hash a file using SHA-384."""

    # Read files in 128 KB chunks to save memory
    # https://eklitzke.org/efficient-file-copying-on-linux
    buf_size: int = 131072

    sha3: sha3_384 = sha3_384()

    # Open the file in binary mode
    with open(file, "rb") as f:
        # Read the file in chunks
        while True:
            data: bytes = f.read(buf_size)
            if not data:
                break
            sha3.update(data)

    # Get the hash of the file
    hash_str: str = sha3.hexdigest()
    return hash_str
