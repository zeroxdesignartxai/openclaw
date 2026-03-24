import unittest

from safe_lyrics.originality_guard import evaluate_originality
from safe_lyrics.prompt_builder import build_generation_prompt
from safe_lyrics.style_indexer import build_style_index


class SafeLyricsTests(unittest.TestCase):
    def test_build_style_index_creates_genre_summary(self) -> None:
        index = build_style_index(
            [
                {
                    "id": "one",
                    "title": "Song One",
                    "artist": "Artist",
                    "genre": "Pop",
                    "lyrics": "City lights shimmer tonight\nWe chase the sound into the dawn",
                }
            ]
        )

        self.assertEqual(index["source_count"], 1)
        self.assertIn("pop", index["genres"])
        self.assertGreaterEqual(len(index["documents"][0]["originality"]["banned_five_grams"]), 1)

    def test_evaluate_originality_rejects_direct_overlap(self) -> None:
        index = build_style_index(
            [
                {
                    "id": "source-1",
                    "title": "Song",
                    "artist": "Artist",
                    "genre": "Pop",
                    "lyrics": "we run into the fire and never look away",
                }
            ]
        )

        result = evaluate_originality("we run into the fire and never look away", index)
        self.assertFalse(result["passed"])
        self.assertEqual(result["closest_source_id"], "source-1")

    def test_prompt_uses_abstract_style_guidance_only(self) -> None:
        style_index = build_style_index(
            [
                {
                    "id": "two",
                    "title": "Song Two",
                    "artist": "Artist",
                    "genre": "Rock",
                    "lyrics": "Broken radios on the floor and summer thunder at the door",
                }
            ]
        )

        prompt = build_generation_prompt(
            genre="Rock",
            topic="surviving heartbreak",
            mood="defiant",
            style_index=style_index,
        )

        self.assertIn("Genre: Rock", prompt)
        self.assertIn("Do not quote, mimic, paraphrase", prompt)
        self.assertNotIn("Broken radios on the floor", prompt)

    def test_pop_prompt_uses_deterministic_song_structure(self) -> None:
        prompt = build_generation_prompt(
            genre="Pop",
            topic="second chances",
            mood="hopeful",
            style_index={"genres": {}, "documents": []},
        )
        self.assertIn("Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus", prompt)


if __name__ == "__main__":
    unittest.main()
