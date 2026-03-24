import json
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path
from unittest.mock import patch

from safe_lyrics import app_state, local_config, web


class WebTests(unittest.TestCase):
    def test_render_page_includes_desktop_saas_sections(self) -> None:
        page = web.render_page(
            values={"provider": "openai", "api_key": "", "genre": "Pop", "topic": "late-night ambition", "mood": "charged"},
            lyrics="Electric City\n\nVerse one",
            originality={"closest_source_id": "sample", "highest_shared_count": 0},
        )
        self.assertIn("LyricMaster AI", page)
        self.assertIn("Compose an original lyric draft", page)
        self.assertIn("Live lyric response", page)
        self.assertIn("Format Output", page)
        self.assertIn("Preview mode", page)

    def test_full_route_flow_supports_login_generation_history_and_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "app_state.json"
            config_path = Path(temp_dir) / "local_config.json"
            with patch.object(app_state, "APP_STATE_PATH", state_path), patch.object(local_config, "LOCAL_CONFIG_PATH", config_path):
                server = web.ThreadingHTTPServer(("127.0.0.1", 0), web.LyricsRequestHandler)
                port = server.server_address[1]
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    cookie_jar = CookieJar()
                    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
                    base_url = f"http://127.0.0.1:{port}"

                    landing = opener.open(f"{base_url}/").read().decode("utf-8")
                    self.assertIn("Masterpiece Lyrics. Zero Copyright Risk.", landing)

                    login_page = opener.open(f"{base_url}/auth/google/mock").read().decode("utf-8")
                    self.assertIn("Continue with Google", login_page)

                    login_payload = urllib.parse.urlencode(
                        {
                            "email": "writer@lyricmaster.ai",
                            "google_id": "google-user-1",
                            "name": "Avery Lane",
                        }
                    ).encode("utf-8")
                    opener.open(f"{base_url}/auth/google/mock", data=login_payload)

                    dashboard = opener.open(f"{base_url}/dashboard").read().decode("utf-8")
                    self.assertIn("build the next draft fast", dashboard)

                    with patch("safe_lyrics.web.generate_safe_lyrics") as mock_generate:
                        mock_generate.return_value = {
                            "lyrics": "Electric City\n\nVerse one in violet light\nChorus calls me home",
                            "originality": {"closest_source_id": None, "highest_shared_count": 0, "highest_overlap_ratio": 0.0},
                            "provider": "openai",
                            "trend_summary": {"available": False},
                            "selected_model": "gpt-4.1-mini",
                        }
                        request = urllib.request.Request(
                            f"{base_url}/api/v1/generate",
                            data=json.dumps(
                                {
                                    "genre": "Synthwave",
                                    "topic": "heartbreak on a midnight drive",
                                    "mood": "cinematic",
                                    "provider": "openai",
                                    "api_key": "test-key",
                                }
                            ).encode("utf-8"),
                            headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
                            method="POST",
                        )
                        stream = opener.open(request).read().decode("utf-8")
                        self.assertIn("event: status", stream)
                        self.assertIn("event: done", stream)
                        self.assertIn("Electric City", stream)

                    history_payload = json.loads(opener.open(f"{base_url}/api/v1/history").read().decode("utf-8"))
                    self.assertEqual(len(history_payload["items"]), 1)
                    self.assertEqual(history_payload["items"][0]["genre"], "Synthwave")

                    subscription_payload = urllib.parse.urlencode({"tier": "pro"}).encode("utf-8")
                    opener.open(f"{base_url}/settings/subscription", data=subscription_payload)
                    me_payload = json.loads(opener.open(f"{base_url}/api/v1/users/me").read().decode("utf-8"))
                    self.assertEqual(me_payload["user"]["tier"], "pro")

                    opener.open(f"{base_url}/auth/logout")
                    login_after_logout = opener.open(f"{base_url}/auth/google/mock").read().decode("utf-8")
                    self.assertIn("Sign in to your writing workspace", login_after_logout)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
