import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from safe_lyrics import google_oauth, local_config


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


class GoogleOAuthTests(unittest.TestCase):
    def test_build_auth_url_includes_scope_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "local_config.json"
            with patch.object(local_config, "LOCAL_CONFIG_PATH", config_path), patch.object(google_oauth, "save_google_oauth_state") as mock_state:
                local_config.save_google_oauth_settings("client-id", "secret", "project-id")
                url = google_oauth.build_google_auth_url()
                self.assertIn("client_id=client-id", url)
                self.assertIn("response_type=code", url)
                mock_state.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_refresh_access_token_returns_project_id(self, mock_urlopen) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "local_config.json"
            with patch.object(local_config, "LOCAL_CONFIG_PATH", config_path), patch.object(google_oauth, "get_google_oauth_config") as mock_config:
                mock_config.return_value = {
                    "client_id": "client-id",
                    "client_secret": "secret",
                    "project_id": "project-id",
                    "tokens": {
                        "refresh_token": "refresh",
                        "expires_at": 0,
                    },
                }
                mock_urlopen.return_value = FakeResponse({"access_token": "token", "expires_in": 3600, "token_type": "Bearer"})
                token, project_id = google_oauth.get_valid_google_access_token()
                self.assertEqual(token, "token")
                self.assertEqual(project_id, "project-id")


if __name__ == "__main__":
    unittest.main()
