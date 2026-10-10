import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT_DIR / "change-feed-ground-truth.csv"

PERSONAS = [
    "bob@horquva-test.local",
    "alice@horquva-test.local",
    "carol@horquva-test.local",
]

SCENARIOS = [
    ("synthetic_departure", "Synthetic persona departure", "Ownership dependency should be reviewed"),
    ("synthetic_departure", "Synthetic persona marked inactive", "Inactive persona should appear in the change feed"),
    ("synthetic_departure", "Mock team membership departure", "Mock ownership mapping should be reviewed"),
    ("synthetic_departure", "Synthetic workflow owner departure", "Dependent workflow ownership should be flagged"),
    ("synthetic_departure", "Synthetic backup owner departure", "Backup coverage should be reviewed"),
    ("model_swap", "AI model configuration changed from model-a to model-b", "Model configuration change should be recorded"),
    ("model_swap", "Mock model provider changed", "Provider dependency should be reviewed"),
    ("model_swap", "Fallback model configuration updated", "Fallback configuration change should be recorded"),
    ("model_swap", "Mock model version updated", "Model version change should be recorded"),
    ("model_swap", "AI workflow model reference replaced", "Workflow model dependency should be reviewed"),
    ("credential_removal", "Mock credential reference removed", "Missing credential should be flagged"),
    ("credential_removal", "Synthetic API token marked unavailable", "Credential dependency should be reviewed"),
    ("credential_removal", "Mock service credential disabled in test data", "Credential status change should be recorded"),
    ("credential_removal", "Workflow credential reference missing", "Workflow should identify the missing reference"),
    ("credential_removal", "Mock integration secret marked expired", "Expired credential should be flagged"),
    ("rate_limit_failure", "Mock API rate limit exceeded", "Rate-limit event should be recorded"),
    ("rate_limit_failure", "Synthetic model request rate limited", "Retry or backoff should be considered"),
    ("rate_limit_failure", "Mock integration quota exhausted", "Quota issue should be recorded"),
    ("rate_limit_failure", "Synthetic API burst limit reached", "Rate-limit response should be reviewed"),
    ("rate_limit_failure", "Mock provider returns rate-limit response", "Provider failure should be visible in test data"),
]

FIELDNAMES = [
    "change_id",
    "timestamp_utc",
    "persona",
    "change_type",
    "platform",
    "description",
    "expected_effect",
]


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()

        for index, scenario in enumerate(SCENARIOS, start=1):
            change_type, description, expected_effect = scenario
            writer.writerow({
                "change_id": f"CHG-{index:03d}",
                "timestamp_utc": timestamp,
                "persona": PERSONAS[(index - 1) % len(PERSONAS)],
                "change_type": change_type,
                "platform": "mock",
                "description": description,
                "expected_effect": expected_effect,
            })

    print(f"Created change feed: {OUTPUT_FILE}")
    print(f"Records written: {len(SCENARIOS)}")
    print("Mode: synthetic mock data only; no live services changed.")


if __name__ == "__main__":
    main()
