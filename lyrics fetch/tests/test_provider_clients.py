import json
import unittest
import urllib.error
from unittest.mock import patch

from safe_lyrics.openai_client import generate_lyrics


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self.payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def close(self) -> None:
        return None


class ProviderClientTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_generate_lyrics_supports_gemini(self, mock_urlopen) -> None:
        mock_urlopen.return_value = FakeResponse(
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": "Original lyric draft",
                                }
                            ]
                        }
                    }
                ]
            }
        )

        result = generate_lyrics("write a song", provider="gemini", api_key="gemini-key")
        self.assertEqual(result, "Original lyric draft")

    @patch("urllib.request.urlopen")
    def test_generate_lyrics_supports_openai_model_override(self, mock_urlopen) -> None:
        mock_urlopen.return_value = FakeResponse({"output_text": "Draft from override"})
        result = generate_lyrics("write a song", provider="openai", api_key="openai-key", model="gpt-4.1")
        self.assertEqual(result, "Draft from override")

    @patch("urllib.request.urlopen")
    def test_generate_lyrics_falls_back_when_gemini_model_is_retired(self, mock_urlopen) -> None:
        retired_error = urllib.error.HTTPError(
            url="https://example.test",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=FakeResponse(
                {
                    "error": {
                        "code": 404,
                        "message": "model retired",
                    }
                }
            ),
        )

        mock_urlopen.side_effect = [
            retired_error,
            FakeResponse(
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "text": "Fallback lyric draft",
                                    }
                                ]
                            }
                        }
                    ]
                }
            ),
        ]

        result = generate_lyrics("write a song", provider="gemini", api_key="gemini-key")
        self.assertEqual(result, "Fallback lyric draft")


if __name__ == "__main__":
    unittest.main()
