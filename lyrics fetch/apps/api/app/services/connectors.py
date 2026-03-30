from typing import List
from sqlalchemy.orm import Session

from app.db import models as dbm


def fetch_candidates(category: str, constraints: dict, db: Session, user_data=None) -> List[dict]:
    # For MVP, pull items for the category; fallback to in-memory defaults
    items = db.query(dbm.Item).filter(dbm.Item.category_id.isnot(None)).all()
    if items:
        return [
            {
                "id": str(it.id),
                "title": it.title,
                "data": it.normalized_json or {},
            }
            for it in items
        ]

    # Default seeded candidates per category
    defaults = {
        "software": [
            {"id": "hubspot-starter", "title": "HubSpot Starter", "data": {"price": 20, "fit": "Small teams"}},
            {"id": "pipedrive", "title": "Pipedrive Essential", "data": {"price": 15, "fit": "Sales-led"}},
        ],
        "electronics": [
            {"id": "macbook-air-m3", "title": "MacBook Air M3", "data": {"price": 1099, "fit": "Lightweight, fast"}},
            {"id": "legion-pro", "title": "Lenovo Legion Pro", "data": {"price": 1499, "fit": "High GPU"}},
        ],
        "service-providers": [
            {"id": "bench", "title": "Bench Accounting", "data": {"price": 299, "fit": "Bookkeeping"}},
            {"id": "toptal", "title": "Toptal", "data": {"price": 80, "fit": "Senior freelancers"}},
        ],
    }
    return defaults.get(category, defaults["software"])
