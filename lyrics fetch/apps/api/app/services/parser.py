from dataclasses import dataclass
import re


@dataclass
class ParsedQuery:
    text: str
    intent: str
    constraints: dict


def parse_query(text: str) -> ParsedQuery:
    lowered = text.lower()
    budget = None
    match = re.search(r"\$?(\d{2,5})", lowered)
    if match:
        budget = int(match.group(1))
    intent = "recommendation" if any(k in lowered for k in ["best", "recommend", "choose"]) else "lookup"
    constraints = {"budget": budget} if budget else {}
    return ParsedQuery(text=text, intent=intent, constraints=constraints)
