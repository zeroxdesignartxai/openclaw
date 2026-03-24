from collections import Counter, defaultdict

from safe_lyrics.text_utils import average, build_ngrams, estimate_syllables, normalize_text, split_lines, tokenize_words, unique

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "i",
    "in",
    "into",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "our",
    "so",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "we",
    "with",
    "you",
    "your",
}


def _top_keywords(words: list[str], limit: int = 12) -> list[str]:
    counts = Counter(word for word in words if len(word) >= 4 and word not in STOP_WORDS)
    return [word for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def _estimate_rhyme_profile(lines: list[str]) -> dict:
    endings = []
    for line in lines:
        words = tokenize_words(line)
        if words:
            endings.append(words[-1][-3:])

    unique_endings = len(set(endings))
    density = 0.0 if not endings else 1 - (unique_endings / len(endings))
    return {
        "ending_samples": unique(endings)[:8],
        "rhyme_density": round(density, 2),
    }


def _estimate_structure(line_count: int) -> str:
    if line_count >= 16:
        return "long-form"
    if line_count >= 8:
        return "verse-like"
    if line_count >= 4:
        return "hook-like"
    return "fragment"


def _summarize_document(entry: dict) -> dict:
    lyrics = entry.get("lyrics", "") if isinstance(entry.get("lyrics"), str) else ""
    normalized = normalize_text(lyrics)
    words = tokenize_words(normalized)
    lines = split_lines(lyrics if lyrics else normalized)
    line_lengths = [len(tokenize_words(line)) for line in lines if tokenize_words(line)]
    syllables = [estimate_syllables(word) for word in words]
    ngrams = unique(build_ngrams(words, 5))

    return {
        "id": entry.get("id"),
        "title": entry.get("title"),
        "artist": entry.get("artist"),
        "genre": entry.get("genre"),
        "stats": {
            "line_count": len(lines),
            "avg_line_words": round(average(line_lengths), 2),
            "avg_word_syllables": round(average(syllables), 2),
            "structure": _estimate_structure(len(lines)),
        },
        "style": {
            "keywords": _top_keywords(words),
            "imagery_hints": _top_keywords([word for word in words if len(word) >= 5], 8),
            **_estimate_rhyme_profile(lines),
        },
        "originality": {
            "banned_five_grams": ngrams,
        },
    }


def build_style_index(entries: list[dict]) -> dict:
    documents = [_summarize_document(entry) for entry in entries]
    grouped: dict[str, dict] = defaultdict(lambda: {
        "source_count": 0,
        "keywords": [],
        "imagery_hints": [],
        "structures": [],
        "avg_line_words": [],
    })

    for document in documents:
        genre_key = normalize_text(document.get("genre") or "unknown")
        genre = grouped[genre_key]
        genre["source_count"] += 1
        genre["keywords"].extend(document["style"]["keywords"])
        genre["imagery_hints"].extend(document["style"]["imagery_hints"])
        genre["structures"].append(document["stats"]["structure"])
        genre["avg_line_words"].append(document["stats"]["avg_line_words"])

    genres = {}
    for genre_key, genre in grouped.items():
        common_structure = Counter(genre["structures"]).most_common(1)[0][0] if genre["structures"] else "verse-like"
        genres[genre_key] = {
            "source_count": genre["source_count"],
            "keywords": _top_keywords(genre["keywords"], 16),
            "imagery_hints": _top_keywords(genre["imagery_hints"], 12),
            "common_structure": common_structure,
            "avg_line_words": round(average(genre["avg_line_words"]), 2),
        }

    return {
        "source_count": len(entries),
        "genres": genres,
        "documents": documents,
    }
