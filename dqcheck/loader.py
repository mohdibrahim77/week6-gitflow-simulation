"""Load CSV files into a list of dict rows."""

import csv
from pathlib import Path


class LoadError(Exception):
    """Raised when a file cannot be loaded as CSV."""


def load_csv(path):
    """Return ``(columns, rows)``; every row is a dict of column -> stripped string."""
    p = Path(path)
    if not p.exists():
        raise LoadError(f"file not found: {p}")
    text = p.read_text(encoding="utf-8")
    reader = csv.DictReader(text.splitlines())
    rows = [{k: v.strip() if isinstance(v, str) else v for k, v in r.items()} for r in reader]
    return list(reader.fieldnames or []), rows
