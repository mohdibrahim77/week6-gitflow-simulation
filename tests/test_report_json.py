import json
import unittest

from dqcheck.report import render_json
from dqcheck.rules import Violation


class RenderJsonTest(unittest.TestCase):
    def test_structure(self):
        v = [Violation("unique", "id", 3, "2", "duplicate of row 2")]
        doc = json.loads(render_json(v, 3))
        self.assertEqual(doc["rows_checked"], 3)
        self.assertFalse(doc["passed"])
        self.assertEqual(doc["violations"][0]["rule"], "unique")
        self.assertEqual(doc["violations"][0]["row"], 3)

    def test_clean(self):
        self.assertTrue(json.loads(render_json([], 1))["passed"])


if __name__ == "__main__":
    unittest.main()
