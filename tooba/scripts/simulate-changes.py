
import csv
from pathlib import Path
from datetime import datetime, timezone

# Repository ke root folder ka path
ROOT_DIR = Path(__file__).resolve().parent.parent

# CSV output file
OUTPUT_FILE = ROOT_DIR / "shared" / "tooba" / "change-feed-ground-truth.csv"

# Sirf synthetic test personas use karein.
# In records se kisi real platform par account changes nahi hote.
CHANGES = [
    {
        "change_id": "CHG-001",
        "persona": "bob@horquva-test.local",
        "change_type": "synthetic_departure",
        "platform": "mock",
        "description": "Simulated departure of a synthetic test persona",
        "expected_effect": "Test workflow should detect the persona status change",
    },
    {
        "change_id": "CHG-002",
        "persona": "alice@horquva-test.local",
        "change_type": "model_swap",
        "platform": "mock",
        "description": "Simulated AI model configuration change",
        "expected_effect": "Test workflow should record the model configuration change",
    },
    {
        "change_id": "CHG-003",
        "persona": "carol@horquva-test.local",
        "change_type": "credential_removal",
        "platform": "mock",
        "description": "Simulated removal of a mock credential reference",
        "expected_effect": "Test workflow should identify the missing mock credential",
    },
]


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "change_id",
        "timestamp_utc",
        "persona",
        "change_type",
        "platform",
        "description",
        "expected_effect",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for change in CHANGES:
            row = change.copy()
            row["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
            writer.writerow(row)

    print(f"Created change feed: {OUTPUT_FILE}")
    print(f"Records written: {len(CHANGES)}")
    print("Mode: mock data only; no live accounts or services were changed.")


if __name__ == "__main__":
    main()