"""
File hashing algorithms.
"""

from hashlib import sha3_384
from pathlib import Path


def hash_in_chunks(file: Path) -> str:
    """Hash a file using SHA-384."""

    # Read files in 64kb chunks to save memory
    buf_size: int = 65536

    sha3: sha3_384 = sha3_384()

    with open(file, "rb") as f:
        while True:
            data: bytes = f.read(buf_size)
            if not data:
                break
            sha3.update(data)

    hash_str: str = sha3.hexdigest()
    return hash_str
