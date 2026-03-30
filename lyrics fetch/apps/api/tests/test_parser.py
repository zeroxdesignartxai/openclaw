from app.services import parser


def test_parse_budget_and_intent():
    parsed = parser.parse_query("best laptop under $1200")
    assert parsed.intent == "recommendation"
    assert parsed.constraints["budget"] == 1200
