"""Render a list of Violation objects for humans or machines."""

import json
from dataclasses import asdict


def render_json(violations, n_rows):
    """Machine-readable report, e.g. for a CI step or a data-quality dashboard."""
    return json.dumps(
        {
            "rows_checked": n_rows,
            "violation_count": len(violations),
            "passed": not violations,
            "violations": [asdict(v) for v in violations],
        },
        indent=2,
    )
