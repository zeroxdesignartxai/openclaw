def pick_best(ranked):
    return ranked[0] if ranked else None


def format_public_answer(top):
    cand = top["candidate"]
    title = cand["title"]
    data = cand.get("data", {})
    meta = {}
    if "price" in data:
        meta["price"] = f"${data['price']}/month starting point"
    if "fit" in data:
        meta["fit"] = data["fit"]
    return title, meta
