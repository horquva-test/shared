import csv
import subprocess
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_FILE = ROOT_DIR / "scripts" / "simulate-changes.py"
CSV_FILE = ROOT_DIR / "change-feed-ground-truth.csv"

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

EXPECTED_TYPES = {
    "synthetic_departure",
    "model_swap",
    "credential_removal",
    "rate_limit_failure",
}


class TestSimulateChanges(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(SCRIPT_FILE)],
            check=True,
            cwd=ROOT_DIR,
        )
        with CSV_FILE.open("r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            cls.columns = reader.fieldnames
            cls.rows = list(reader)

    def test_csv_has_expected_columns(self):
        self.assertEqual(self.columns, EXPECTED_COLUMNS)

    def test_csv_has_twenty_records(self):
        self.assertEqual(len(self.rows), 20)

    def test_personas_are_synthetic_and_allowed(self):
        personas = {row["persona"] for row in self.rows}
        self.assertEqual(personas, ALLOWED_PERSONAS)

    def test_change_ids_are_unique(self):
        ids = [row["change_id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_required_fields_are_filled(self):
        for row in self.rows:
            for column in EXPECTED_COLUMNS:
                with self.subTest(change_id=row.get("change_id"), column=column):
                    self.assertTrue(row[column].strip())

    def test_all_four_change_types_are_present(self):
        actual_types = {row["change_type"] for row in self.rows}
        self.assertEqual(actual_types, EXPECTED_TYPES)

    def test_all_records_are_mock_only(self):
        self.assertTrue(all(row["platform"] == "mock" for row in self.rows))


if __name__ == "__main__":
    unittest.main(verbosity=2)
