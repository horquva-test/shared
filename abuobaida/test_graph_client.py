import unittest
from unittest.mock import patch, MagicMock
from graph_client import EntraGraphClient, EntraAuthError


def resp(status_code, json_data=None, headers=None, text=""):
    m = MagicMock()
    m.status_code = status_code
    m.json.return_value = json_data or {}
    m.headers = headers or {}
    m.text = text
    m.raise_for_status.side_effect = None
    return m


class TestAuthenticate(unittest.TestCase):
    @patch("graph_client.requests.post")
    def test_successful_auth(self, mock_post):
        mock_post.return_value = resp(200, {"access_token": "fake-token"})
        c = EntraGraphClient("id", "secret", "tenant")
        c.authenticate()
        self.assertEqual(c.token, "fake-token")

    @patch("graph_client.requests.post")
    def test_auth_failure_raises(self, mock_post):
        mock_post.return_value = resp(401, text="bad client secret")
        c = EntraGraphClient("id", "wrong", "tenant")
        with self.assertRaises(EntraAuthError):
            c.authenticate()


class TestFetchUsers(unittest.TestCase):
    @patch("graph_client.requests.get")
    def test_successful_fetch_single_page(self, mock_get):
        mock_get.return_value = resp(200, {"value": [{"id": "1"}, {"id": "2"}]})
        c = EntraGraphClient("id", "secret", "tenant")
        c.token = "fake-token"
        result = c.fetch_users()
        self.assertEqual(len(result["entities"]), 2)
        self.assertFalse(result["limited_visibility"])

    @patch("graph_client.requests.get")
    def test_pagination_follows_nextlink(self, mock_get):
        page1 = resp(200, {"value": [{"id": "1"}], "@odata.nextLink": "https://graph.microsoft.com/v1.0/users?skip=1"})
        page2 = resp(200, {"value": [{"id": "2"}]})
        mock_get.side_effect = [page1, page2]
        c = EntraGraphClient("id", "secret", "tenant")
        c.token = "fake-token"
        result = c.fetch_users()
        self.assertEqual(len(result["entities"]), 2)
        self.assertEqual(mock_get.call_count, 2)

    def test_empty_result(self):
        with patch("graph_client.requests.get", return_value=resp(200, {"value": []})):
            c = EntraGraphClient("id", "secret", "tenant")
            c.token = "fake-token"
            result = c.fetch_users()
            self.assertEqual(result["entities"], [])
            self.assertFalse(result["limited_visibility"])

    @patch("graph_client.time.sleep", return_value=None)
    @patch("graph_client.requests.get")
    def test_429_then_success(self, mock_get, mock_sleep):
        throttled = resp(429, headers={"Retry-After": "1"})
        ok = resp(200, {"value": [{"id": "1"}]})
        mock_get.side_effect = [throttled, ok]
        c = EntraGraphClient("id", "secret", "tenant")
        c.token = "fake-token"
        result = c.fetch_users()
        self.assertEqual(len(result["entities"]), 1)
        mock_sleep.assert_called_once()

    @patch("graph_client.requests.post")
    @patch("graph_client.requests.get")
    def test_401_triggers_reauth_then_succeeds(self, mock_get, mock_post):
        expired = resp(401)
        ok = resp(200, {"value": [{"id": "1"}]})
        mock_get.side_effect = [expired, ok]
        mock_post.return_value = resp(200, {"access_token": "new-token"})
        c = EntraGraphClient("id", "secret", "tenant")
        c.token = "stale-token"
        result = c.fetch_users()
        self.assertEqual(len(result["entities"]), 1)
        self.assertEqual(c.token, "new-token")

    @patch("graph_client.requests.get")
    def test_403_returns_limited_visibility(self, mock_get):
        mock_get.return_value = resp(403)
        c = EntraGraphClient("id", "secret", "tenant")
        c.token = "fake-token"
        result = c.fetch_users()
        self.assertEqual(result, {"limited_visibility": True, "entities": []})


class TestFetchGroupsAndApps(unittest.TestCase):
    @patch("graph_client.requests.get")
    def test_fetch_groups(self, mock_get):
        mock_get.return_value = resp(200, {"value": [{"id": "g1"}] * 6})
        c = EntraGraphClient("id", "secret", "tenant")
        c.token = "fake-token"
        self.assertEqual(len(c.fetch_groups()["entities"]), 6)

    @patch("graph_client.requests.get")
    def test_fetch_applications(self, mock_get):
        mock_get.return_value = resp(200, {"value": [{"id": "a1"}] * 5})
        c = EntraGraphClient("id", "secret", "tenant")
        c.token = "fake-token"
        self.assertEqual(len(c.fetch_applications()["entities"]), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
