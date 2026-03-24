import re
from statistics import mean

WORD_RE = re.compile(r"[a-z0-9']+")
NON_TEXT_RE = re.compile(r"[^\w'\s]+", re.UNICODE)


def normalize_text(value: str) -> str:
    lowered = value.lower().replace("\r", "")
    cleaned = NON_TEXT_RE.sub(" ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


def tokenize_words(value: str) -> list[str]:
    return WORD_RE.findall(normalize_text(value))


def split_lines(value: str) -> list[str]:
    return [normalize_text(line) for line in re.split(r"\n+", value) if normalize_text(line)]


def build_ngrams(words: list[str], size: int) -> list[str]:
    return [" ".join(words[index : index + size]) for index in range(0, len(words) - size + 1)]


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def average(values: list[float]) -> float:
    return 0.0 if not values else float(mean(values))


def estimate_syllables(word: str) -> int:
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
      return 0

    trimmed = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", cleaned)
    trimmed = re.sub(r"^y", "", trimmed)
    groups = re.findall(r"[aeiouy]{1,2}", trimmed)
    return max(1, len(groups))
