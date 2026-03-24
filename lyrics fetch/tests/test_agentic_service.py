import unittest
from unittest.mock import patch

from safe_lyrics.service import generate_safe_lyrics


class AgenticServiceTests(unittest.TestCase):
    @patch("safe_lyrics.service.load_style_index")
    @patch("safe_lyrics.service.get_trend_report")
    @patch("safe_lyrics.service.generate_lyrics")
    def test_agentic_mode_returns_workflow_trace(self, mock_generate, mock_trends, mock_style_index) -> None:
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
            "Title direction: Electric rise",
            "Electric Rise\n\nVerse one\nVerse two\nChorus\nBridge",
            "strengths\nweaknesses\nexact revision goals",
            "Electric Rise\n\nVerse one brightens the skyline\nVerse two sharpens the hunger\nChorus opens wide and memorable\nBridge turns inward then erupts",
        ]

        result = generate_safe_lyrics("pop", "ambition", "bright", provider="openai", api_key="x", agentic_mode=True)
        self.assertEqual(result["draft_mode"], "agent-workflow")
        self.assertIn("workflow_trace", result)
        self.assertIn("plan", result["workflow_trace"])


if __name__ == "__main__":
    unittest.main()
