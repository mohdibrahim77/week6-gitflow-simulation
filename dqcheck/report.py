"""Render a list of Violation objects for humans or machines."""

from collections import Counter


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
