from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.query import QueryRequest, QueryResponse
from app.services import parser, router, connectors, scorer, formatter, pipeline
from app.db import models as dbm


router_api = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router_api.post("/query", response_model=QueryResponse)
def handle_query(payload: QueryRequest, db: Session = Depends(get_db)):
    if not payload.input.strip():
        raise HTTPException(status_code=400, detail="Input required")

    parsed = parser.parse_query(payload.input)
    category = router.detect_category(payload.category, parsed, db)
    constraints = router.extract_constraints(parsed)

    candidates = connectors.fetch_candidates(category, constraints, db, user_data=payload.user_data)

    # Optional internal tokenize-to-cluster pipeline
    cluster_info = pipeline.run_cluster_pipeline(category, payload.user_data, parsed) if payload.user_data else None

    ranked = scorer.score_candidates(parsed, candidates, constraints, cluster_info)
    top = formatter.pick_best(ranked)

    if not top:
        raise HTTPException(status_code=404, detail="No answer found")

    answer_text, meta = formatter.format_public_answer(top)

    q = dbm.Query(
        raw_input=payload.input,
        detected_category=category,
        detected_intent=parsed.intent,
        constraints_json=constraints,
        answer_text=answer_text,
        answer_meta_json=meta,
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    return QueryResponse(query_id=q.id, answer=answer_text, meta=meta)
