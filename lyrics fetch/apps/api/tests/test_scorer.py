from app.services import scorer, parser


def test_scores_sort_desc():
    p = parser.parse_query("best crm under 30")
    candidates = [
        {"id": "a", "title": "A", "data": {"price": 50, "fit": "x"}},
        {"id": "b", "title": "B", "data": {"price": 20, "fit": "y"}},
    ]
    ranked = scorer.score_candidates(p, candidates, {"budget": 30})
    assert ranked[0]["candidate"]["id"] == "b"
