import json
import secrets
import uuid
from datetime import UTC, datetime
from pathlib import Path

APP_STATE_PATH = Path("data/app_state.json")
FREE_TIER_LIMIT = 5


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _month_key(value: datetime | None = None) -> str:
    current = value or _utc_now()
    return current.strftime("%Y-%m")


def _default_state() -> dict:
    return {
        "users": [],
        "sessions": [],
        "generations": [],
        "plagiarism_logs": [],
    }


def load_app_state() -> dict:
    if not APP_STATE_PATH.exists():
        return _default_state()

    payload = json.loads(APP_STATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return _default_state()

    state = _default_state()
    for key in state:
        value = payload.get(key, state[key])
        state[key] = value if isinstance(value, list) else state[key]
    return state


def save_app_state(state: dict) -> dict:
    APP_STATE_PATH.write_text(f"{json.dumps(state, indent=2)}\n", encoding="utf-8")
    return state


def create_or_update_user(*, email: str, google_id: str, name: str = "") -> dict:
    normalized_email = email.strip().lower()
    normalized_google_id = google_id.strip() or normalized_email
    if not normalized_email:
        raise RuntimeError("Email is required.")

    state = load_app_state()
    now = _utc_now().isoformat()
    for user in state["users"]:
        if user.get("email") == normalized_email or user.get("google_id") == normalized_google_id:
            user["email"] = normalized_email
            user["google_id"] = normalized_google_id
            user["name"] = name.strip() or user.get("name", "")
            user["last_login_at"] = now
            save_app_state(state)
            return user

    user = {
        "id": str(uuid.uuid4()),
        "email": normalized_email,
        "google_id": normalized_google_id,
        "name": name.strip(),
        "tier": "free",
        "role": "user",
        "created_at": now,
        "last_login_at": now,
    }
    state["users"].append(user)
    save_app_state(state)
    return user


def get_user(user_id: str) -> dict | None:
    state = load_app_state()
    for user in state["users"]:
        if user.get("id") == user_id:
            return user
    return None


def create_session(user_id: str) -> str:
    state = load_app_state()
    token = secrets.token_urlsafe(32)
    state["sessions"] = [session for session in state["sessions"] if session.get("user_id") != user_id]
    state["sessions"].append(
        {
            "token": token,
            "user_id": user_id,
            "created_at": _utc_now().isoformat(),
        }
    )
    save_app_state(state)
    return token


def get_user_by_session(token: str) -> dict | None:
    if not token.strip():
        return None

    state = load_app_state()
    session = next((item for item in state["sessions"] if item.get("token") == token), None)
    if not session:
        return None
    return next((user for user in state["users"] if user.get("id") == session.get("user_id")), None)


def delete_session(token: str) -> None:
    state = load_app_state()
    state["sessions"] = [session for session in state["sessions"] if session.get("token") != token]
    save_app_state(state)


def list_generations(user_id: str) -> list[dict]:
    state = load_app_state()
    rows = [row for row in state["generations"] if row.get("user_id") == user_id]
    return sorted(rows, key=lambda item: item.get("created_at", ""), reverse=True)


def count_generations_for_month(user_id: str, month_key: str | None = None) -> int:
    target_month = month_key or _month_key()
    return sum(1 for row in list_generations(user_id) if str(row.get("created_at", "")).startswith(target_month))


def get_generation_allowance(user: dict) -> dict:
    tier = str(user.get("tier", "free"))
    if tier == "pro":
        return {
            "allowed": True,
            "tier": tier,
            "limit": None,
            "used": count_generations_for_month(str(user.get("id", ""))),
            "remaining": None,
        }

    used = count_generations_for_month(str(user.get("id", "")))
    remaining = max(FREE_TIER_LIMIT - used, 0)
    return {
        "allowed": remaining > 0,
        "tier": tier,
        "limit": FREE_TIER_LIMIT,
        "used": used,
        "remaining": remaining,
    }


def record_generation(
    *,
    user_id: str,
    genre: str,
    topic: str,
    mood: str,
    power: str = "",
    lyrics: str,
    provider: str,
    selected_model: str,
    originality: dict,
) -> dict:
    state = load_app_state()
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "genre": genre.strip(),
        "topic": topic.strip(),
        "mood": mood.strip(),
        "power": power.strip(),
        "lyrics": lyrics,
        "provider": provider,
        "selected_model": selected_model,
        "created_at": _utc_now().isoformat(),
        "originality": originality,
    }
    state["generations"].append(row)
    save_app_state(state)
    return row


def record_plagiarism_log(*, generation_id: str, flagged_phrase: str, resolved: bool) -> dict:
    state = load_app_state()
    row = {
        "id": str(uuid.uuid4()),
        "generation_id": generation_id,
        "flagged_phrase": flagged_phrase,
        "resolved": resolved,
        "created_at": _utc_now().isoformat(),
    }
    state["plagiarism_logs"].append(row)
    save_app_state(state)
    return row


def update_user_tier(user_id: str, tier: str) -> dict:
    normalized_tier = tier.strip().lower()
    if normalized_tier not in {"free", "pro"}:
        raise RuntimeError("Tier must be free or pro.")

    state = load_app_state()
    for user in state["users"]:
        if user.get("id") == user_id:
            user["tier"] = normalized_tier
            save_app_state(state)
            return user
    raise RuntimeError("User not found.")


def delete_user_account(user_id: str) -> None:
    state = load_app_state()
    generation_ids = {row.get("id") for row in state["generations"] if row.get("user_id") == user_id}
    state["users"] = [user for user in state["users"] if user.get("id") != user_id]
    state["sessions"] = [session for session in state["sessions"] if session.get("user_id") != user_id]
    state["generations"] = [row for row in state["generations"] if row.get("user_id") != user_id]
    state["plagiarism_logs"] = [row for row in state["plagiarism_logs"] if row.get("generation_id") not in generation_ids]
    save_app_state(state)
