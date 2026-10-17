import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout

from dqcheck.cli import main
from tests.helpers import write_tmp


class CliTest(unittest.TestCase):
    """Exercise main() end to end with temporary files."""

    def run_cli(self, csv_text, rules):
        csv_path = write_tmp(csv_text)
        rules_path = write_tmp(json.dumps(rules), suffix=".json")
        self.addCleanup(os.remove, csv_path)
        self.addCleanup(os.remove, rules_path)
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = main([csv_path, "--rules", rules_path])
        return code, out.getvalue()

    def test_clean_file(self):
        code, out = self.run_cli("id\n1\n2\n", [{"column": "id", "rule": "unique"}])
        self.assertEqual(code, 0)
        self.assertIn("2 rows checked, 0 violation(s)", out)

    def test_violations_are_printed(self):
        code, out = self.run_cli("id\n1\n1\n", [{"column": "id", "rule": "unique"}])
        self.assertEqual(code, 1)  # non-zero so CI jobs / schedulers can fail on bad data
        self.assertIn("duplicate of row 1", out)

    def test_invalid_rules_json(self):
        csv_path = write_tmp("id\n1\n")
        rules_path = write_tmp('[{"column": "id", "rule": "matches"', suffix=".json")  # truncated JSON
        self.addCleanup(os.remove, csv_path)
        self.addCleanup(os.remove, rules_path)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main([csv_path, "--rules", rules_path]), 2)
        self.assertIn("invalid rules file", err.getvalue())

    def test_examples_run(self):
        with redirect_stdout(io.StringIO()) as out:
            code = main(["examples/customers.csv", "--rules", "examples/customers_rules.json"])
        self.assertEqual(code, 1)
        self.assertIn("8 rows checked", out.getvalue())

    def test_missing_file(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["nope.csv", "--rules", "nope.json"]), 2)


if __name__ == "__main__":
    unittest.main()
