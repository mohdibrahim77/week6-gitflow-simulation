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
    """Non-empty values in ``column`` must not repeat (blanks are ``not_null``'s job)."""
    seen, out = {}, []
    for i, r in enumerate(rows, 1):
        value = r.get(column)
        if _is_empty(value):
            continue
        if value in seen:
            out.append(Violation("unique", column, i, value, f"duplicate of row {seen[value]}"))
        else:
            seen[value] = i
    return out


def in_range(rows, column, min=None, max=None):
    """Numeric values must lie within ``[min, max]``; empty values are skipped."""
    out = []
    for i, r in enumerate(rows, 1):
        value = r.get(column)
        if _is_empty(value):
            continue
        try:
            number = float(value)
        except ValueError:
            out.append(Violation("in_range", column, i, value, "not a number"))
            continue
        if (min is not None and number < min) or (max is not None and number > max):
            out.append(Violation("in_range", column, i, value, f"outside [{min}, {max}]"))
    return out


def matches(rows, column, pattern):
    """Non-empty values must fully match the regular expression ``pattern``."""
    rx = re.compile(pattern)
    return [
        Violation("matches", column, i, r.get(column), f"does not match {pattern}")
        for i, r in enumerate(rows, 1)
        if not _is_empty(r.get(column)) and not rx.fullmatch(r.get(column))
    ]


RULES = {"not_null": not_null, "unique": unique, "in_range": in_range, "matches": matches}


def run_rules(rows, columns, config):
    """Run every rule spec in ``config`` (a list of dicts) and collect the violations.

    A spec looks like ``{"column": "age", "rule": "in_range", "min": 0, "max": 120}``.
    """
    out = []
    for spec in config:
        params = dict(spec)
        column, name = params.pop("column"), params.pop("rule")
        if name not in RULES:
            raise ValueError(f"unknown rule: {name}")
        if column not in columns:
            raise ValueError(f"unknown column: {column}")
        out.extend(RULES[name](rows, column, **params))
    return out
