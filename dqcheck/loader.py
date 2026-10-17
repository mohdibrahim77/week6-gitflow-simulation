"""Load CSV files into a list of dict rows."""

import csv
from pathlib import Path


class LoadError(Exception):
    """Raised when a file cannot be loaded as CSV."""


def load_csv(path, delimiter=None):
    """Return ``(columns, rows)``; every row is a dict of column -> stripped string.

    The delimiter (``, ; | TAB``) is sniffed from the first 4 KB unless given.
    A UTF-8 byte-order mark (common in Excel exports) is removed.
    """
    p = Path(path)
    if not p.exists():
        raise LoadError(f"file not found: {p}")
    text = p.read_text(encoding="utf-8-sig")
    if not text.strip():
        raise LoadError(f"file is empty: {p}")
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:4096], delimiters=",;|\t").delimiter
        except csv.Error:
            delimiter = ","
    reader = csv.DictReader(text.splitlines(), delimiter=delimiter)
    rows = [{k: v.strip() if isinstance(v, str) else v for k, v in r.items()} for r in reader]
    return list(reader.fieldnames or []), rows
