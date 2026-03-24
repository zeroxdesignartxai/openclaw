from safe_lyrics.prompt_builder import build_generation_prompt


def build_planner_prompt(genre: str, topic: str, mood: str, style_index: dict, trend_summary: dict) -> str:
    base = build_generation_prompt(genre, topic, mood, style_index, trend_summary)
    return f"""{base}

You are the planning stage in a lyric-writing workflow.
Do not write the final song.

Return a compact writing plan with these sections:
- Title direction
- Verse imagery
- Chorus hook idea
- Bridge turn
- Word palette"""


def build_critic_prompt(plan: str, lyrics: str, trend_summary: dict) -> str:
    trend_focus = ", ".join(trend_summary.get("top_themes", [])[:3]) or "none"
    return f"""You are the critique stage in a lyric-writing workflow.

Review this song draft for originality, memorability, clarity, emotional specificity, and hook strength.
Also consider these safe trend signals: {trend_focus}

Plan:
{plan}

Draft:
{lyrics}

Return:
- strengths
- weaknesses
- exact revision goals"""


def build_revision_prompt(plan: str, lyrics: str, critique: str) -> str:
    return f"""You are the revision stage in a lyric-writing workflow.

Rewrite this into a stronger final song.
Keep it fully original.
Do not quote or imitate existing lyrics.

Plan:
{plan}

Current draft:
{lyrics}

Critique:
{critique}

Output:
- title first
- 2 verses
- 1 chorus
- 1 bridge
- stronger hook
- tighter imagery
- polished phrasing"""
