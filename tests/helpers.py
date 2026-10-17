import os
import tempfile


def write_tmp(text, suffix=".csv", encoding="utf-8"):
    """Write text to a temporary file and return its path (caller deletes it)."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding=encoding, newline="") as f:
        f.write(text)
    return path
