from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import SessionLocal
from app.models.query import QueryResponse
from app.db import models as dbm


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/result/{query_id}", response_model=QueryResponse)
def get_result(query_id: UUID, db: Session = Depends(get_db)):
    q = db.query(dbm.Query).filter(dbm.Query.id == query_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Result not found")
    return QueryResponse(query_id=q.id, answer=q.answer_text, meta=q.answer_meta_json or {})
