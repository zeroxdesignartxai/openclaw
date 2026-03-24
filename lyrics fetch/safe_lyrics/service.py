import json
from pathlib import Path

from safe_lyrics.agent_workflow import build_critic_prompt, build_planner_prompt, build_revision_prompt
from safe_lyrics.formatter import format_lyrics
from safe_lyrics.google_oauth import get_valid_google_access_token
from safe_lyrics.local_config import get_default_provider, get_provider_api_key
from safe_lyrics.openai_client import generate_lyrics
from safe_lyrics.originality_guard import evaluate_originality
from safe_lyrics.prompt_builder import build_generation_prompt
from safe_lyrics.trend_analyzer import build_trend_summary, load_trend_index

STYLE_INDEX_PATH = Path("data/style_index.json")
OPENAI_DRAFT_MODELS = ("gpt-4.1-mini", "gpt-4.1")
GEMINI_DRAFT_MODELS = ("gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash")


def load_style_index() -> dict:
    return json.loads(STYLE_INDEX_PATH.read_text(encoding="utf-8"))


def get_trend_report(genre: str) -> dict:
    return build_trend_summary(load_trend_index(), genre)


def format_generated_lyrics(lyrics: str) -> dict:
    if not lyrics.strip():
        raise RuntimeError("Lyrics are required.")

    formatted = format_lyrics(lyrics)
    return {
        "formatted_lyrics": formatted,
        "line_count": len([line for line in formatted.splitlines() if line.strip()]),
    }


def _get_candidate_models(provider: str, multi_model: bool) -> tuple[str, ...]:
    normalized_provider = provider.strip().lower()
    if normalized_provider == "gemini":
        return GEMINI_DRAFT_MODELS if multi_model else (GEMINI_DRAFT_MODELS[0],)
    if normalized_provider == "openai":
        return OPENAI_DRAFT_MODELS if multi_model else (OPENAI_DRAFT_MODELS[0],)
    raise RuntimeError(f"Unsupported provider: {provider}")


def _score_candidate(lyrics: str, formatted_lyrics: str, originality: dict, trend_summary: dict) -> float:
    words = [word for word in formatted_lyrics.replace("\n", " ").split(" ") if word]
    unique_ratio = (len(set(word.lower() for word in words)) / len(words)) if words else 0
    line_count = len([line for line in formatted_lyrics.splitlines() if line.strip()])
    structure_bonus = 0.15 if line_count >= 12 else 0.0
    trend_terms = {
        *trend_summary.get("top_themes", []),
        *trend_summary.get("top_moods", []),
        *trend_summary.get("top_production", []),
    }
    trend_hits = sum(1 for term in trend_terms if term and term.lower() in formatted_lyrics.lower())
    originality_score = 1 - originality.get("highest_overlap_ratio", 0.0)
    return round((unique_ratio * 0.45) + (min(line_count, 20) / 20 * 0.2) + (min(trend_hits, 6) / 6 * 0.2) + (originality_score * 0.15) + structure_bonus, 4)


def _run_agentic_draft(
    *,
    genre: str,
    topic: str,
    mood: str,
    style_index: dict,
    trend_summary: dict,
    provider: str,
    api_key: str,
    oauth_token: str | None,
    google_project_id: str | None,
    multi_model: bool,
) -> dict:
    workflow_model = _get_candidate_models(provider, multi_model)[0]
    plan = generate_lyrics(
        build_planner_prompt(genre, topic, mood, style_index, trend_summary),
        provider=provider,
        api_key=api_key,
        model=workflow_model,
        oauth_token=oauth_token,
        google_project_id=google_project_id,
    )
    draft = generate_lyrics(
        build_generation_prompt(genre, topic, mood, style_index, trend_summary) + f"\n\nWriting plan:\n{plan}",
        provider=provider,
        api_key=api_key,
        model=workflow_model,
        oauth_token=oauth_token,
        google_project_id=google_project_id,
    )
    critique = generate_lyrics(
        build_critic_prompt(plan, draft, trend_summary),
        provider=provider,
        api_key=api_key,
        model=workflow_model,
        oauth_token=oauth_token,
        google_project_id=google_project_id,
    )
    revised = generate_lyrics(
        build_revision_prompt(plan, draft, critique),
        provider=provider,
        api_key=api_key,
        model=workflow_model,
        oauth_token=oauth_token,
        google_project_id=google_project_id,
    )
    return {
        "plan": plan,
        "draft": draft,
        "critique": critique,
        "revised": revised,
        "workflow_model": workflow_model,
    }


def generate_safe_lyrics(
    genre: str,
    topic: str,
    mood: str,
    provider: str = "openai",
    api_key: str | None = None,
    multi_model: bool = False,
    agentic_mode: bool = False,
) -> dict:
    if not genre.strip() or not topic.strip() or not mood.strip():
        raise RuntimeError("Genre, topic, and mood are all required.")

    resolved_provider = provider.strip() or get_default_provider()
    resolved_api_key = api_key.strip() if api_key and api_key.strip() else get_provider_api_key(resolved_provider)
    oauth_token = None
    google_project_id = None
    if resolved_provider == "gemini" and not resolved_api_key:
        try:
            oauth_token, google_project_id = get_valid_google_access_token()
        except RuntimeError:
            oauth_token = None
            google_project_id = None

    style_index = load_style_index()
    trend_summary = get_trend_report(genre.strip())
    prompt = build_generation_prompt(
        genre=genre.strip(),
        topic=topic.strip(),
        mood=mood.strip(),
        style_index=style_index,
        trend_summary=trend_summary,
    )

    last_originality = None
    best_candidate = None
    candidate_models = _get_candidate_models(resolved_provider, multi_model)

    if agentic_mode:
        workflow = _run_agentic_draft(
            genre=genre.strip(),
            topic=topic.strip(),
            mood=mood.strip(),
            style_index=style_index,
            trend_summary=trend_summary,
            provider=resolved_provider,
            api_key=resolved_api_key,
            oauth_token=oauth_token,
            google_project_id=google_project_id,
            multi_model=multi_model,
        )
        lyrics = workflow["revised"]
        originality = evaluate_originality(lyrics, style_index)
        last_originality = originality
        if originality["passed"]:
            formatted = format_generated_lyrics(lyrics)
            return {
                "lyrics": formatted["formatted_lyrics"],
                "originality": originality,
                "prompt": prompt,
                "provider": resolved_provider,
                "trend_summary": trend_summary,
                "selected_model": workflow["workflow_model"],
                "candidate_score": _score_candidate(lyrics, formatted["formatted_lyrics"], originality, trend_summary),
                "draft_mode": "agent-workflow",
                "candidate_models": [workflow["workflow_model"]],
                "workflow_trace": {
                    "plan": workflow["plan"],
                    "critique": workflow["critique"],
                },
            }

    for model_name in candidate_models:
        for _ in range(1, 3):
            lyrics = generate_lyrics(
                prompt,
                provider=resolved_provider,
                api_key=resolved_api_key,
                model=model_name,
                oauth_token=oauth_token,
                google_project_id=google_project_id,
            )
            originality = evaluate_originality(lyrics, style_index)
            last_originality = originality
            if not originality["passed"]:
                continue

            formatted = format_generated_lyrics(lyrics)
            candidate = {
                "lyrics": formatted["formatted_lyrics"],
                "originality": originality,
                "prompt": prompt,
                "provider": resolved_provider,
                "trend_summary": trend_summary,
                "selected_model": model_name,
                "candidate_score": _score_candidate(lyrics, formatted["formatted_lyrics"], originality, trend_summary),
            }
            if best_candidate is None or candidate["candidate_score"] > best_candidate["candidate_score"]:
                best_candidate = candidate
            break

    if best_candidate is not None:
        if multi_model:
            best_candidate["draft_mode"] = "multi-model"
            best_candidate["candidate_models"] = list(candidate_models)
        else:
            best_candidate["draft_mode"] = "single-model"
            best_candidate["candidate_models"] = [best_candidate["selected_model"]]
        return best_candidate

    raise RuntimeError(
        "The system could not produce lyrics that passed the originality guard across the current draft attempts. "
        f"Closest source: {last_originality['closest_source_id'] or 'unknown'}; "
        f"shared 5-grams: {last_originality['highest_shared_count']}; "
        f"overlap ratio: {last_originality['highest_overlap_ratio']}"
    )
