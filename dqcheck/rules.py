"""Validation rules. Every rule takes the loaded rows and returns a list of Violation."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    rule: str
    column: str
    row: int  # 1-based data row (header not counted)
    value: str
    message: str


def _is_empty(value):
    return value is None or str(value).strip() == ""


def not_null(rows, column):
    """Every row must have a value in ``column``."""
    return [
        Violation("not_null", column, i, "", "value is missing")
        for i, r in enumerate(rows, 1)
        if _is_empty(r.get(column))
    ]


def unique(rows, column):
    """Values in ``column`` must not repeat."""
    seen, out = {}, []
    for i, r in enumerate(rows, 1):
        value = r.get(column)
        if value in seen:
            out.append(Violation("unique", column, i, value, f"duplicate of row {seen[value]}"))
        else:
            seen[value] = i
    return out
