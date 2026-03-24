import json
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

from safe_lyrics.local_config import get_google_oauth_config, save_google_oauth_state, save_google_oauth_tokens

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/generative-language.retriever",
]


def get_redirect_uri(host: str = "127.0.0.1", port: int = 8000) -> str:
    return f"http://{host}:{port}/oauth/google/callback"


def build_google_auth_url(host: str = "127.0.0.1", port: int = 8000) -> str:
    oauth = get_google_oauth_config()
    client_id = oauth.get("client_id", "")
    if not client_id:
        raise RuntimeError("Google OAuth client ID is not configured.")

    state = secrets.token_urlsafe(24)
    save_google_oauth_state(state)
    params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": get_redirect_uri(host, port),
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )
    return f"{GOOGLE_AUTH_URL}?{params}"


def handle_google_oauth_callback(code: str, state: str, host: str = "127.0.0.1", port: int = 8000) -> dict:
    oauth = get_google_oauth_config()
    expected_state = oauth.get("pending_state", "")
    if not expected_state or state != expected_state:
        raise RuntimeError("Google OAuth state did not match.")

    client_id = oauth.get("client_id", "")
    client_secret = oauth.get("client_secret", "")
    if not client_id or not client_secret:
        raise RuntimeError("Google OAuth client credentials are not configured.")

    payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": get_redirect_uri(host, port),
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google OAuth token exchange failed: {error.code} {body}") from error

    tokens = {
        "access_token": data.get("access_token", ""),
        "refresh_token": data.get("refresh_token", oauth.get("tokens", {}).get("refresh_token", "")),
        "expires_at": int(time.time()) + int(data.get("expires_in", 0)),
        "token_type": data.get("token_type", "Bearer"),
    }
    save_google_oauth_tokens(tokens)
    return tokens


def get_valid_google_access_token() -> tuple[str, str]:
    oauth = get_google_oauth_config()
    tokens = oauth.get("tokens", {})
    project_id = oauth.get("project_id", "")
    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")
    expires_at = int(tokens.get("expires_at", 0))

    if access_token and expires_at > int(time.time()) + 60:
        return access_token, project_id

    if not refresh_token:
        raise RuntimeError("Google OAuth is not connected yet.")

    client_id = oauth.get("client_id", "")
    client_secret = oauth.get("client_secret", "")
    payload = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google OAuth token refresh failed: {error.code} {body}") from error

    refreshed = {
        "access_token": data.get("access_token", ""),
        "refresh_token": refresh_token,
        "expires_at": int(time.time()) + int(data.get("expires_in", 0)),
        "token_type": data.get("token_type", "Bearer"),
    }
    save_google_oauth_tokens(refreshed)
    return refreshed["access_token"], project_id
