
import csv
import subprocess
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_FILE = ROOT_DIR / "scripts" / "simulate-changes.py"
CSV_FILE = ROOT_DIR / "shared" / "tooba" / "change-feed-ground-truth.csv"

EXPECTED_COLUMNS = [
    "change_id",
    "timestamp_utc",
    "persona",
    "change_type",
    "platform",
    "description",
    "expected_effect",
]

ALLOWED_PERSONAS = {
    "bob@horquva-test.local",
    "alice@horquva-test.local",
    "carol@horquva-test.local",
}


class TestSimulateChanges(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generate a fresh CSV using the simulation script.
        subprocess.run(
            [sys.executable, str(SCRIPT_FILE)],
            check=True,
            cwd=ROOT_DIR,
        )

        with CSV_FILE.open(
            "r", newline="", encoding="utf-8"
        ) as csv_file:
            cls.reader = csv.DictReader(csv_file)
            cls.columns = cls.reader.fieldnames
            cls.rows = list(cls.reader)

    def test_csv_has_expected_columns(self):
        self.assertEqual(self.columns, EXPECTED_COLUMNS)

    def test_csv_has_three_records(self):
        self.assertEqual(len(self.rows), 3)

    def test_personas_are_synthetic_and_unique(self):
        personas = [row["persona"] for row in self.rows]

        self.assertEqual(len(set(personas)), 3)
        self.assertTrue(set(personas).issubset(ALLOWED_PERSONAS))

    def test_change_ids_are_unique(self):
        change_ids = [row["change_id"] for row in self.rows]

        self.assertEqual(len(set(change_ids)), len(change_ids))

    def test_required_fields_are_not_empty(self):
        for row in self.rows:
            for column in EXPECTED_COLUMNS:
                with self.subTest(
                    change_id=row.get("change_id"),
                    column=column,
                ):
                    self.assertTrue(row[column].strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)