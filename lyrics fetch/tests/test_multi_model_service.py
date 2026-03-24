import unittest
from unittest.mock import patch

from safe_lyrics.service import generate_safe_lyrics


class MultiModelServiceTests(unittest.TestCase):
    @patch("safe_lyrics.service.load_style_index")
    @patch("safe_lyrics.service.get_trend_report")
    @patch("safe_lyrics.service.generate_lyrics")
    def test_multi_model_mode_selects_best_candidate(self, mock_generate, mock_trends, mock_style_index) -> None:
        mock_style_index.return_value = {"genres": {}, "documents": []}
        mock_trends.return_value = {
            "genre": "pop",
            "available": True,
            "top_themes": ["ambition"],
            "top_moods": ["bright"],
            "top_production": ["wide chorus"],
            "writing_brief": {"theme_focus": ["ambition"], "mood_focus": ["bright"], "production_focus": ["wide chorus"]},
        }
        mock_generate.side_effect = [
            "title\n\nshort line",
            "Title\n\nVerse one burns bright tonight\nVerse two keeps the skyline alive\nChorus lifts the whole room higher\nBridge turns the pressure into fire",
        ]

        result = generate_safe_lyrics("pop", "ambition", "bright", provider="openai", api_key="x", multi_model=True)
        self.assertEqual(result["draft_mode"], "multi-model")
        self.assertIn("selected_model", result)
        self.assertTrue(result["lyrics"])


if __name__ == "__main__":
    unittest.main()
