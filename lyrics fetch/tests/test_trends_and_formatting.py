import unittest

from safe_lyrics.formatter import format_lyrics
from safe_lyrics.prompt_builder import build_generation_prompt
from safe_lyrics.style_indexer import build_style_index
from safe_lyrics.trend_analyzer import build_trend_index, build_trend_summary


class TrendAndFormattingTests(unittest.TestCase):
    def test_build_trend_index_groups_by_genre(self) -> None:
        trend_index = build_trend_index(
            [
                {
                    "platform": "spotify",
                    "title": "One",
                    "artist": "Artist",
                    "genre": "Pop",
                    "rank": 2,
                    "days_on_chart": 12,
                    "momentum": 0.9,
                    "themes": ["ambition", "night drive"],
                    "moods": ["euphoric"],
                    "production": ["big hook"],
                },
                {
                    "platform": "tiktok",
                    "title": "Two",
                    "artist": "Artist",
                    "genre": "Pop",
                    "rank": 1,
                    "days_on_chart": 5,
                    "momentum": 0.95,
                    "themes": ["ambition"],
                    "moods": ["euphoric", "confident"],
                    "production": ["big hook", "short refrain"],
                },
            ]
        )

        summary = build_trend_summary(trend_index, "Pop")
        self.assertTrue(summary["available"])
        self.assertIn("ambition", summary["top_themes"])
        self.assertIn("euphoric", summary["top_moods"])

    def test_format_lyrics_normalizes_spacing_and_sections(self) -> None:
        formatted = format_lyrics("verse 1: midnight sirens\n\n\nwe run fast\nCHORUS: BURN BRIGHT")
        self.assertIn("Verse 1: midnight sirens", formatted)
        self.assertIn("We run fast", formatted)
        self.assertIn("Chorus: BURN BRIGHT", formatted)
        self.assertNotIn("\n\n\n", formatted)

    def test_prompt_includes_trend_intelligence(self) -> None:
        style_index = build_style_index(
            [
                {
                    "id": "base",
                    "title": "Base",
                    "artist": "Artist",
                    "genre": "Pop",
                    "lyrics": "Skyline pulses in the dusk and restless engines call my name",
                }
            ]
        )
        trend_summary = {
            "available": True,
            "top_themes": ["ambition", "escape"],
            "top_moods": ["euphoric"],
            "top_production": ["wide chorus"],
            "writing_brief": {
                "theme_focus": ["ambition"],
                "mood_focus": ["euphoric"],
                "production_focus": ["wide chorus"],
            },
        }

        prompt = build_generation_prompt("Pop", "proving yourself", "charged", style_index, trend_summary)
        self.assertIn("Trend intelligence", prompt)
        self.assertIn("ambition", prompt)
        self.assertIn("wide chorus", prompt)


if __name__ == "__main__":
    unittest.main()
