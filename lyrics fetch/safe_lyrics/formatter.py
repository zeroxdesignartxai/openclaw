import re


SECTION_LABELS = ("verse", "chorus", "bridge", "pre-chorus", "outro", "intro")


def format_lyrics(raw_lyrics: str) -> str:
    lines = [line.rstrip() for line in raw_lyrics.replace("\r", "").split("\n")]
    collapsed = []
    blank_streak = 0

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            blank_streak += 1
            if blank_streak <= 1:
                collapsed.append("")
            continue

        blank_streak = 0
        collapsed.append(_format_line(line))

    while collapsed and not collapsed[0]:
        collapsed.pop(0)
    while collapsed and not collapsed[-1]:
        collapsed.pop()

    return "\n".join(collapsed)


def _format_line(line: str) -> str:
    normalized = re.sub(r"\s+", " ", line).strip()
    lowered = normalized.lower()
    for section in SECTION_LABELS:
        if lowered.startswith(section):
            return _title_case_section(normalized)

    if normalized.isupper() and len(normalized) > 4:
        return normalized.title()

    return normalized[0].upper() + normalized[1:] if normalized else normalized


def _title_case_section(line: str) -> str:
    if ":" in line:
        left, right = line.split(":", 1)
        return f"{left.strip().title()}: {right.strip()}" if right.strip() else f"{left.strip().title()}:"
    return line.title()
