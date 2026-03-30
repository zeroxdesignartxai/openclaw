from app.services import router, parser


def test_detects_electronics():
    p = parser.parse_query("best laptop for editing")
    cat = router.detect_category(None, p, db=None)
    assert cat == "electronics"
