
import json
from pathlib import Path

users = [
    {
        "id": f"user-{i:03}",
        "displayName": f"Test User {i:03}",
        "mail": f"testuser{i:03}@horquva-test.local",
        "accountEnabled": True
    }
    for i in range(1, 31)
]

groups = [
    {
        "id": f"group-{i:02}",
        "displayName": f"Test Group {i:02}",
        "members": [
            users[j]["id"]
            for j in range(len(users))
            if j % 6 == i - 1
        ]
    }
    for i in range(1, 7)
]

apps = [
    {
        "id": f"app-{i:02}",
        "displayName": f"Test App {i:02}"
    }
    for i in range(1, 6)
]

aliases = [
    {
        "userId": "user-001",
        "alias": "testalias1@horquva-test.local"
    },
    {
        "userId": "user-002",
        "alias": "testalias2@horquva-test.local"
    },
    {
        "userId": "user-003",
        "alias": "testalias3@horquva-test.local"
    }
]

data = {
    "source": "MOCK",
    "users": users,
    "groups": groups,
    "apps": apps,
    "aliases": aliases
}

Path("mock_entra_data.json").write_text(
    json.dumps(data, indent=2),
    encoding="utf-8"
)

print("Mock data created successfully.")
print("Users:", len(users))
print("Groups:", len(groups))
print("Apps:", len(apps))
print("Aliases:", len(aliases))
