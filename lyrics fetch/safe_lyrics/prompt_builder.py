from safe_lyrics.text_utils import normalize_text

STRUCTURE_MAP = {
    "pop": "Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus",
    "synthwave": "Verse 1, Pre-Chorus, Chorus, Verse 2, Chorus, Bridge, Chorus",
    "country": "Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus",
    "r&b": "Verse 1, Pre-Chorus, Chorus, Verse 2, Chorus, Bridge, Chorus",
    "trap": "Intro, Verse 1, Hook, Verse 2, Hook, Outro",
}

POWER_MAP = {
    "symphonic": "complex, layered systems",
    "indonesian": "region-specific configs and environments",
    "melodic": "readable, maintainable fixes",
    "brutal": "aggressive debugging and deep root cause work",
    "technical": "low-level, precise, detailed fixes",
    "progressive": "forward-looking, scalable solutions",
    "slamming": "minimal, fast, direct fixes",
    "blackened": "security-focused, hardened fixes",
    "downtempo": "slow, cautious, high-validation approach",
    "christian": "safe, ethical, conservative changes",
}


def resolve_structure_for_genre(genre: str) -> str:
    return STRUCTURE_MAP.get(normalize_text(genre), "Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus")


def _resolve_power_line(power: str | None) -> str:
    if not power or not power.strip():
        return "Neutral — balanced, versatile writing."

    normalized = normalize_text(power)
    descriptor = POWER_MAP.get(normalized)
    if descriptor:
        return f"{power.strip()} — {descriptor}. Reflect this in arrangement, pacing, and imagery without copying source text."

    return f"{power.strip()} — interpret creatively while keeping the song original and well-structured."


def build_generation_prompt(
    genre: str,
    topic: str,
    mood: str,
    style_index: dict,
    trend_summary: dict | None = None,
    power: str | None = None,
) -> str:
    genre_profile = style_index.get("genres", {}).get(normalize_text(genre))
    target_structure = resolve_structure_for_genre(genre)

    if genre_profile:
        profile_text = "\n".join(
            [
                f"Genre profile keywords: {', '.join(genre_profile['keywords']) or 'none'}",
                f"Imagery hints: {', '.join(genre_profile['imagery_hints']) or 'none'}",
                f"Common structure: {genre_profile['common_structure']}",
                f"Target structure for this request: {target_structure}",
                f"Average line length: {genre_profile['avg_line_words']} words",
            ]
        )
    else:
        profile_text = (
            "No genre profile was found. Use the requested genre in an original way.\n"
            f"Target structure for this request: {target_structure}"
        )

    trend_text = "No trend report is available. Prioritize originality over imitation."
    if trend_summary and trend_summary.get("available"):
        writing_brief = trend_summary.get("writing_brief", {})
        trend_text = "\n".join(
            [
                f"Trend themes: {', '.join(trend_summary.get('top_themes', [])) or 'none'}",
                f"Trend moods: {', '.join(trend_summary.get('top_moods', [])) or 'none'}",
                f"Trend production cues: {', '.join(trend_summary.get('top_production', [])) or 'none'}",
                f"Recommended focus: themes={', '.join(writing_brief.get('theme_focus', [])) or 'none'}; moods={', '.join(writing_brief.get('mood_focus', [])) or 'none'}; production={', '.join(writing_brief.get('production_focus', [])) or 'none'}",
            ]
        )

    power_text = _resolve_power_line(power)

    return f"""Write completely original song lyrics.

User request:
- Genre: {genre}
- Topic: {topic}
- Mood: {mood}

Safety rules:
- Do not quote, mimic, paraphrase, or continue any existing song.
- Do not reuse recognizable lyric phrases.
- Do not reference specific copyrighted lyrics.
- Use only abstract style guidance, never source text.

Style guidance:
{profile_text}

Beat power:
{power_text}

Trend intelligence:
{trend_text}

Output requirements:
- Produce one song with a title line first.
- Follow this exact section order: {target_structure}.
- Keep the language vivid, emotionally specific, and memorable.
- Make the lyrics feel polished and performance-ready.
- Avoid placeholders and avoid mentioning these instructions."""
