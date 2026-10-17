"""Command-line entry point:  python -m dqcheck data.csv --rules rules.json

Exit codes: 0 = clean, 1 = violations found, 2 = CSV or rules file could not be loaded.
"""

import argparse
import json
import sys

from . import __version__
from .loader import LoadError, load_csv
from .report import render_text
from .rules import run_rules


def build_parser():
    p = argparse.ArgumentParser(prog="dqcheck", description="Data-quality checks for CSV files.")
    p.add_argument("csv", help="CSV file to check")
    p.add_argument("--rules", required=True, help="JSON file containing a list of rule specs")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        columns, rows = load_csv(args.csv)
    except LoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        with open(args.rules, encoding="utf-8") as f:
            config = json.load(f)
        violations = run_rules(rows, columns, config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: invalid rules file {args.rules}: {exc}", file=sys.stderr)
        return 2
    print(render_text(violations, len(rows)))
    return 1 if violations else 0
