from safe_lyrics.text_utils import build_ngrams, normalize_text, tokenize_words

MAX_SHARED_FIVE_GRAMS = 0
MAX_OVERLAP_RATIO = 0.08


def evaluate_originality(candidate_lyrics: str, style_index: dict) -> dict:
    candidate_words = tokenize_words(normalize_text(candidate_lyrics))
    candidate_grams = set(build_ngrams(candidate_words, 5))
    highest_shared_count = 0
    highest_overlap_ratio = 0.0
    closest_source_id = None
    flagged_phrase = None

    for document in style_index.get("documents", []):
        source_grams = set(document.get("originality", {}).get("banned_five_grams", []))
        shared_grams = candidate_grams & source_grams
        shared_count = len(shared_grams)
        overlap_ratio = 0.0 if not candidate_grams else shared_count / len(candidate_grams)

        if shared_count > highest_shared_count or overlap_ratio > highest_overlap_ratio:
            highest_shared_count = shared_count
            highest_overlap_ratio = overlap_ratio
            closest_source_id = document.get("id")
            flagged_phrase = next(iter(shared_grams), None)

    passed = highest_shared_count <= MAX_SHARED_FIVE_GRAMS and highest_overlap_ratio <= MAX_OVERLAP_RATIO
    return {
        "passed": passed,
        "highest_shared_count": highest_shared_count,
        "highest_overlap_ratio": round(highest_overlap_ratio, 3),
        "closest_source_id": closest_source_id,
        "flagged_phrase": flagged_phrase.replace("|", " ") if flagged_phrase else "",
    }
