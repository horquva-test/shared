"""
Runner: uses live Microsoft Graph credentials from .env if present,
otherwise falls back to the existing mock_entra_data.json (Clarification 4:
mock-first, continue on mock and document the delay if live isn't ready).
"""
import json
import os
import sys
from pathlib import Path


def load_env(path=".env"):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = val.strip()


def run_mock():
    from entra_connector import load_entra_data, validate_entra_data
    data = load_entra_data()
    report = validate_entra_data(data)
    report["mode"] = "MOCK"
    return report


def run_live():
    from graph_client import EntraGraphClient, EntraAuthError
    client_id = os.environ.get("ENTRA_CLIENT_ID")
    client_secret = os.environ.get("ENTRA_CLIENT_SECRET")
    tenant_id = os.environ.get("ENTRA_TENANT_ID")
    if not (client_id and client_secret and tenant_id):
        return None

    client = EntraGraphClient(client_id, client_secret, tenant_id)
    try:
        client.authenticate()
    except EntraAuthError as e:
        print(f"LIVE FAIL (auth): {e}", file=sys.stderr)
        return None

    users = client.fetch_users()
    groups = client.fetch_groups()
    apps = client.fetch_applications()

    report = {
        "mode": "LIVE",
        "source": "LIVE",
        "users": len(users["entities"]),
        "groups": len(groups["entities"]),
        "apps": len(apps["entities"]),
        "aliases": None,
        "limited_visibility": {
            "users": users["limited_visibility"],
            "groups": groups["limited_visibility"],
            "apps": apps["limited_visibility"],
        },
    }
    return report


def main():
    load_env()
    report = run_live()
    if report is None:
        print("No live credentials in .env (ENTRA_CLIENT_ID/SECRET/TENANT_ID) or auth failed -- using mock.")
        report = run_mock()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
