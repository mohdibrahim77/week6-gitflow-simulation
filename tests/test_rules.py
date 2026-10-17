import unittest

from dqcheck.rules import not_null, unique

ROWS = [
    {"id": "1", "email": "a@x.com", "age": "34"},
    {"id": "2", "email": "", "age": "-5"},
    {"id": "2", "email": "c@x", "age": "abc"},
]


class NotNullTest(unittest.TestCase):
    def test_flags_missing(self):
        v = not_null(ROWS, "email")
        self.assertEqual([x.row for x in v], [2])


class UniqueTest(unittest.TestCase):
    def test_flags_duplicates(self):
        v = unique(ROWS, "id")
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].row, 3)
        self.assertIn("row 2", v[0].message)

    def test_blank_values_are_not_duplicates(self):  # regression test for #5
        rows = [{"code": ""}, {"code": "  "}, {"code": None}, {"code": "A"}]
        self.assertEqual(unique(rows, "code"), [])


class InRangeTest(unittest.TestCase):
    def test_out_of_range_and_not_numeric(self):
        from dqcheck.rules import in_range
        v = in_range(ROWS, "age", min=0, max=120)
        self.assertEqual([(x.row, x.message) for x in v], [(2, "outside [0, 120]"), (3, "not a number")])


class MatchesTest(unittest.TestCase):
    def test_regex(self):
        from dqcheck.rules import matches
        v = matches(ROWS, "email", r"[^@]+@[^@]+\.[a-z]+")
        self.assertEqual([x.row for x in v], [3])  # row 2 is empty -> not_null's job


class RunRulesTest(unittest.TestCase):
    def test_config(self):
        from dqcheck.rules import run_rules
        cfg = [{"column": "id", "rule": "unique"}, {"column": "age", "rule": "in_range", "min": 0}]
        self.assertEqual(len(run_rules(ROWS, ["id", "email", "age"], cfg)), 3)

    def test_unknown_rule_and_column(self):
        from dqcheck.rules import run_rules
        with self.assertRaises(ValueError):
            run_rules(ROWS, ["id"], [{"column": "id", "rule": "nope"}])
        with self.assertRaises(ValueError):
            run_rules(ROWS, ["id"], [{"column": "zzz", "rule": "unique"}])


if __name__ == "__main__":
    unittest.main()
