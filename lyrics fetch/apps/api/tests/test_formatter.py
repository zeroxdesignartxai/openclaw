from app.services import formatter


def test_format_meta_fields():
    top = {"candidate": {"title": "HubSpot", "data": {"price": 20, "fit": "Small teams"}}}
    answer, meta = formatter.format_public_answer(top)
    assert answer == "HubSpot"
    assert meta["price"] == "$20/month starting point"
