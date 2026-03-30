from sqlalchemy.orm import Session
from app.db import models as dbm


def seed(db: Session):
    if db.query(dbm.Category).count() > 0:
        return

    cats = [
        dbm.Category(slug="software", name="Software Tools", pipeline_enabled=True),
        dbm.Category(slug="electronics", name="Electronics", pipeline_enabled=False),
        dbm.Category(slug="service-providers", name="Service Providers", pipeline_enabled=False),
    ]
    db.add_all(cats)
    db.commit()
