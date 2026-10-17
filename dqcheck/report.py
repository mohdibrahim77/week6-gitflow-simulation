"""Render a list of Violation objects for humans or machines."""

import json
from collections import Counter
from dataclasses import asdict


def render_text(violations, n_rows):
    """Aligned table grouped by rule, followed by a per-rule summary."""
    lines = []
    for v in sorted(violations, key=lambda v: (v.row, v.column)):
        lines.append(f"row {v.row:>4}  {v.column:<14} {v.rule:<9} {v.message}")
    if violations:
        lines.append("")
        for rule, count in sorted(Counter(v.rule for v in violations).items()):
            lines.append(f"  {rule:<9} {count:>3}")
    status = "PASS" if not violations else "FAIL"
    lines.append(f"{status}: {n_rows} rows checked, {len(violations)} violation(s)")
    return "\n".join(lines)


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
