from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.db import models as dbm


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    return db.query(dbm.Category).all()


@router.post("/categories")
def create_category(payload: dict, db: Session = Depends(get_db)):
    cat = dbm.Category(
        slug=payload.get("slug"),
        name=payload.get("name"),
        pipeline_enabled=payload.get("pipeline_enabled", False),
        public_output_template=payload.get("public_output_template", None),
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/connectors")
def list_connectors(db: Session = Depends(get_db)):
    return db.query(dbm.Connector).all()


@router.post("/connectors")
def create_connector(payload: dict, db: Session = Depends(get_db)):
    conn = dbm.Connector(
        name=payload.get("name"),
        type=payload.get("type"),
        config_json=payload.get("config_json") or {},
        active=payload.get("active", True),
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return conn


@router.get("/rules")
def list_rules(db: Session = Depends(get_db)):
    return db.query(dbm.AdminRule).all()


@router.post("/rules")
def create_rule(payload: dict, db: Session = Depends(get_db)):
    rule = dbm.AdminRule(
        category_id=payload.get("category_id"),
        key=payload.get("key"),
        value_json=payload.get("value_json") or {},
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
