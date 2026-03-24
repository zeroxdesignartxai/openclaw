import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from safe_lyrics import local_config


class LocalConfigTests(unittest.TestCase):
    def test_save_and_clear_provider_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "local_config.json"
            with patch.object(local_config, "LOCAL_CONFIG_PATH", config_path):
                local_config.save_provider_api_key("gemini", "abc123")
                self.assertEqual(local_config.get_provider_api_key("gemini"), "abc123")

                written = json.loads(config_path.read_text(encoding="utf-8"))
                self.assertEqual(written["provider_keys"]["gemini"], "abc123")

                local_config.clear_provider_api_key("gemini")
                self.assertEqual(local_config.get_provider_api_key("gemini"), "")


if __name__ == "__main__":
    unittest.main()
