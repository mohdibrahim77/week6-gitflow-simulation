import os
import unittest

from dqcheck.loader import LoadError, load_csv
from tests.helpers import write_tmp


class LoadCsvTest(unittest.TestCase):
    def load(self, text, **kw):
        path = write_tmp(text, **kw)
        self.addCleanup(os.remove, path)
        return load_csv(path)

    def test_comma(self):
        cols, rows = self.load("id,name\n1, Asha \n2,Ravi\n")
        self.assertEqual(cols, ["id", "name"])
        self.assertEqual(rows, [{"id": "1", "name": "Asha"}, {"id": "2", "name": "Ravi"}])

    def test_semicolon_is_sniffed(self):
        cols, rows = self.load("id;city\n1;Pune\n2;Delhi\n")
        self.assertEqual(cols, ["id", "city"])
        self.assertEqual(rows[1]["city"], "Delhi")

    def test_bom_is_stripped(self):
        cols, _ = self.load("id,name\n1,a\n", encoding="utf-8-sig")
        self.assertEqual(cols[0], "id")

    def test_missing_file(self):
        with self.assertRaises(LoadError):
            load_csv("does/not/exist.csv")

    def test_empty_file(self):
        with self.assertRaises(LoadError):
            self.load("   \n")


if __name__ == "__main__":
    unittest.main()
