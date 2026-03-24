import json
from collections import Counter, defaultdict
from pathlib import Path

from safe_lyrics.text_utils import normalize_text

PLATFORM_SIGNAL_PATH = Path("data/platform_signals.json")
TREND_INDEX_PATH = Path("data/trend_index.json")
PLATFORM_WEIGHTS = {
    "spotify": 1.0,
    "apple_music": 0.95,
    "youtube": 0.9,
    "tiktok": 1.05,
}


def load_platform_signals() -> list[dict]:
    if not PLATFORM_SIGNAL_PATH.exists():
        return []
    return json.loads(PLATFORM_SIGNAL_PATH.read_text(encoding="utf-8"))


def _score_entry(entry: dict) -> float:
    rank = max(1, int(entry.get("rank", 100)))
    momentum = float(entry.get("momentum", 0.5))
    days = max(1, int(entry.get("days_on_chart", 1)))
    platform_weight = PLATFORM_WEIGHTS.get(normalize_text(str(entry.get("platform", ""))), 0.8)
    freshness = 1 / (1 + (days / 30))
    rank_signal = max(0.05, (101 - min(rank, 100)) / 100)
    return round(platform_weight * ((rank_signal * 0.65) + (momentum * 0.25) + (freshness * 0.10)), 4)


def build_trend_index(entries: list[dict]) -> dict:
    by_genre: dict[str, dict] = defaultdict(
        lambda: {
            "songs": [],
            "themes": Counter(),
            "moods": Counter(),
            "production": Counter(),
            "scores": [],
        }
    )

    for entry in entries:
        genre = normalize_text(str(entry.get("genre", "unknown")))
        score = _score_entry(entry)
        genre_bucket = by_genre[genre]
        genre_bucket["songs"].append(
            {
                "platform": entry.get("platform", "unknown"),
                "title": entry.get("title", "Unknown"),
                "artist": entry.get("artist", "Unknown"),
                "score": score,
            }
        )
        genre_bucket["scores"].append(score)
        genre_bucket["themes"].update(normalize_text(value) for value in entry.get("themes", []) if value)
        genre_bucket["moods"].update(normalize_text(value) for value in entry.get("moods", []) if value)
        genre_bucket["production"].update(normalize_text(value) for value in entry.get("production", []) if value)

    genres = {}
    for genre, bucket in by_genre.items():
        ranked_songs = sorted(bucket["songs"], key=lambda item: item["score"], reverse=True)
        genres[genre] = {
            "top_songs": ranked_songs[:5],
            "top_themes": [label for label, _ in bucket["themes"].most_common(6)],
            "top_moods": [label for label, _ in bucket["moods"].most_common(6)],
            "top_production": [label for label, _ in bucket["production"].most_common(6)],
            "average_score": round(sum(bucket["scores"]) / len(bucket["scores"]), 4) if bucket["scores"] else 0.0,
        }

    return {
        "source_count": len(entries),
        "genres": genres,
    }


def write_trend_index(index: dict) -> None:
    TREND_INDEX_PATH.write_text(f"{json.dumps(index, indent=2)}\n", encoding="utf-8")


def load_trend_index() -> dict:
    if TREND_INDEX_PATH.exists():
        return json.loads(TREND_INDEX_PATH.read_text(encoding="utf-8"))

    index = build_trend_index(load_platform_signals())
    write_trend_index(index)
    return index


def build_trend_summary(index: dict, genre: str) -> dict:
    genre_key = normalize_text(genre)
    genre_report = index.get("genres", {}).get(genre_key)
    if not genre_report:
        return {
            "genre": genre,
            "available": False,
            "message": "No trend report is available for this genre yet.",
        }

    return {
        "genre": genre,
        "available": True,
        "top_themes": genre_report.get("top_themes", []),
        "top_moods": genre_report.get("top_moods", []),
        "top_production": genre_report.get("top_production", []),
        "top_songs": genre_report.get("top_songs", []),
        "average_score": genre_report.get("average_score", 0.0),
        "writing_brief": {
            "theme_focus": genre_report.get("top_themes", [])[:3],
            "mood_focus": genre_report.get("top_moods", [])[:3],
            "production_focus": genre_report.get("top_production", [])[:3],
        },
    }
