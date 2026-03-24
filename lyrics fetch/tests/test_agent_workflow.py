import unittest

from safe_lyrics.agent_workflow import build_critic_prompt, build_planner_prompt, build_revision_prompt
from safe_lyrics.style_indexer import build_style_index


class AgentWorkflowTests(unittest.TestCase):
    def test_planner_prompt_requests_plan_not_song(self) -> None:
        style_index = build_style_index(
            [
                {
                    "id": "x",
                    "title": "X",
                    "artist": "Y",
                    "genre": "Pop",
                    "lyrics": "neon shadows call me home through midnight rain",
                }
            ]
        )
        trend_summary = {"available": True, "top_themes": ["ambition"], "top_moods": ["bright"], "top_production": ["wide chorus"], "writing_brief": {}}
        prompt = build_planner_prompt("Pop", "late night focus", "charged", style_index, trend_summary)
        self.assertIn("Do not write the final song", prompt)
        self.assertIn("Title direction", prompt)

    def test_critic_and_revision_prompts_include_inputs(self) -> None:
        critique = build_critic_prompt("plan", "draft", {"top_themes": ["ambition"]})
        revision = build_revision_prompt("plan", "draft", "make the hook stronger")
        self.assertIn("strengths", critique)
        self.assertIn("make the hook stronger", revision)


if __name__ == "__main__":
    unittest.main()
