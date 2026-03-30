from app.db import models as dbm
from sqlalchemy.orm import Session


DEFAULT_CATEGORY = "software"


def detect_category(explicit: str | None, parsed, db: Session) -> str:
    if explicit:
        return explicit
    text = parsed.text.lower()
    if any(k in text for k in ["laptop", "phone", "camera"]):
        return "electronics"
    if any(k in text for k in ["crm", "saas", "software", "tool"]):
        return "software"
    if any(k in text for k in ["agency", "provider", "service"]):
        return "service-providers"
    return DEFAULT_CATEGORY


def extract_constraints(parsed) -> dict:
    return parsed.constraints or {}
