import unittest

from dqcheck.report import render_text
from dqcheck.rules import Violation

V = [
    Violation("unique", "id", 3, "2", "duplicate of row 2"),
    Violation("not_null", "email", 2, "", "value is missing"),
]


class RenderTextTest(unittest.TestCase):
    def test_sorted_by_row_with_summary(self):
        out = render_text(V, 3).splitlines()
        self.assertTrue(out[0].startswith("row    2  email"))
        self.assertTrue(out[1].startswith("row    3  id"))
        self.assertIn("  not_null    1", out)
        self.assertEqual(out[-1], "FAIL: 3 rows checked, 2 violation(s)")

    def test_clean(self):
        self.assertEqual(render_text([], 5), "PASS: 5 rows checked, 0 violation(s)")


if __name__ == "__main__":
    unittest.main()
