from typing import List


def score_candidates(parsed, candidates: List[dict], constraints: dict, cluster_info=None):
    budget = constraints.get("budget")
    results = []
    for idx, c in enumerate(candidates):
        price = c["data"].get("price")
        base = 100 - idx  # deterministic fallback
        relevance = 80 if parsed.intent == "recommendation" else 60
        price_fit = 0
        if price and budget:
            price_fit = max(0, 40 - abs(price - budget) / budget * 40)
        total = base + relevance + price_fit
        results.append({"candidate": c, "score": total})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
