
import unittest

from entra_connector import load_entra_data, validate_entra_data


class TestEntraConnector(unittest.TestCase):

    def test_data_counts(self):
        data = load_entra_data()
        report = validate_entra_data(data)

        self.assertEqual(report["users"], 30)
        self.assertEqual(report["groups"], 6)
        self.assertEqual(report["apps"], 5)
        self.assertEqual(report["aliases"], 3)
        self.assertTrue(report["valid"])

    def test_mock_source(self):
        data = load_entra_data()
        self.assertEqual(data["source"], "MOCK")


if __name__ == "__main__":
    unittest.main()
