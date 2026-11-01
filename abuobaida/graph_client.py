"""
Microsoft Graph API client for the Entra connector.
Authenticates with OAuth client credentials, fetches users/groups/applications
with @odata.nextLink pagination, and handles 429/401/403 per the plan's spec.
"""
import time
import requests


class EntraAuthError(Exception):
    pass


class EntraGraphClient:
    def __init__(self, client_id, client_secret, tenant_id, base_url="https://graph.microsoft.com/v1.0"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.base_url = base_url
        self.token = None

    def authenticate(self):
        """Client-credentials flow. Raises EntraAuthError on failure."""
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        res = requests.post(url, data=data, timeout=15)
        if res.status_code != 200:
            raise EntraAuthError(f"Auth failed: {res.status_code} {res.text[:200]}")
        self.token = res.json()["access_token"]

    def _headers(self):
        if not self.token:
            raise EntraAuthError("Not authenticated. Call authenticate() first.")
        return {"Authorization": f"Bearer {self.token}"}

    def _get(self, url, _retried_401=False, _attempt=0):
        """GET with 429 backoff, 401 refresh (once), 403 -> limited_visibility marker."""
        res = requests.get(url, headers=self._headers(), timeout=20)

        if res.status_code == 429:
            if _attempt >= 5:
                raise RuntimeError(f"Rate limited after 5 retries: {url}")
            retry_after = int(res.headers.get("Retry-After", 2 ** _attempt))
            time.sleep(retry_after)
            return self._get(url, _retried_401, _attempt + 1)

        if res.status_code == 401 and not _retried_401:
            self.authenticate()
            return self._get(url, True, _attempt)

        if res.status_code == 403:
            return {"_limited_visibility": True}

        res.raise_for_status()
        return res.json()

    def _fetch_paginated(self, entity_name):
        url = f"{self.base_url}/{entity_name}"
        all_items = []
        while url:
            page = self._get(url)
            if page.get("_limited_visibility"):
                return {"limited_visibility": True, "entities": []}
            all_items.extend(page.get("value", []))
            url = page.get("@odata.nextLink")
        return {"limited_visibility": False, "entities": all_items}

    def fetch_users(self):
        return self._fetch_paginated("users")

    def fetch_groups(self):
        return self._fetch_paginated("groups")

    def fetch_applications(self):
        return self._fetch_paginated("applications")
