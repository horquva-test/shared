
import json
from pathlib import Path


def load_entra_data(file_path="mock_entra_data.json"):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    for key in ["users", "groups", "apps", "aliases"]:
        if key not in data:
            raise ValueError(f"Missing required section: {key}")

    return data


def validate_entra_data(data):
    report = {
        "source": data.get("source", "UNKNOWN"),
        "users": len(data["users"]),
        "groups": len(data["groups"]),
        "apps": len(data["apps"]),
        "aliases": len(data["aliases"]),
    }

    report["valid"] = (
        report["users"] == 30
        and report["groups"] == 6
        and report["apps"] == 5
        and report["aliases"] == 3
    )

    return report


if __name__ == "__main__":
    data = load_entra_data()
    report = validate_entra_data(data)
    print(json.dumps(report, indent=2))
