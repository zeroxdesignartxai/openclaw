import json
from pathlib import Path

LOCAL_CONFIG_PATH = Path("data/local_config.json")


def load_local_config() -> dict:
    if not LOCAL_CONFIG_PATH.exists():
        return {}

    return json.loads(LOCAL_CONFIG_PATH.read_text(encoding="utf-8"))


def get_default_provider() -> str:
    return str(load_local_config().get("provider", "openai"))


def get_default_api_key() -> str:
    config = load_local_config()
    provider = str(config.get("provider", "openai"))
    provider_keys = config.get("provider_keys", {})
    if isinstance(provider_keys, dict) and provider in provider_keys:
        return str(provider_keys.get(provider, ""))
    return str(config.get("api_key", ""))


def get_provider_api_key(provider: str) -> str:
    config = load_local_config()
    provider_keys = config.get("provider_keys", {})
    normalized_provider = provider.strip().lower() or "openai"
    if isinstance(provider_keys, dict):
        return str(provider_keys.get(normalized_provider, ""))
    return ""


def save_provider_api_key(provider: str, api_key: str) -> dict:
    normalized_provider = provider.strip().lower() or "openai"
    config = load_local_config()
    provider_keys = config.get("provider_keys", {})
    if not isinstance(provider_keys, dict):
        provider_keys = {}

    provider_keys[normalized_provider] = api_key.strip()
    config["provider"] = normalized_provider
    config["provider_keys"] = provider_keys
    config["api_key"] = api_key.strip()
    LOCAL_CONFIG_PATH.write_text(f"{json.dumps(config, indent=2)}\n", encoding="utf-8")
    return config


def clear_provider_api_key(provider: str) -> dict:
    normalized_provider = provider.strip().lower() or "openai"
    config = load_local_config()
    provider_keys = config.get("provider_keys", {})
    if not isinstance(provider_keys, dict):
        provider_keys = {}

    provider_keys.pop(normalized_provider, None)
    config["provider_keys"] = provider_keys
    if str(config.get("provider", "openai")) == normalized_provider:
        config["api_key"] = ""
    LOCAL_CONFIG_PATH.write_text(f"{json.dumps(config, indent=2)}\n", encoding="utf-8")
    return config


def get_google_oauth_config() -> dict:
    config = load_local_config()
    oauth = config.get("google_oauth", {})
    return oauth if isinstance(oauth, dict) else {}


def save_google_oauth_settings(client_id: str, client_secret: str, project_id: str) -> dict:
    config = load_local_config()
    oauth = get_google_oauth_config()
    oauth["client_id"] = client_id.strip()
    oauth["client_secret"] = client_secret.strip()
    oauth["project_id"] = project_id.strip()
    config["google_oauth"] = oauth
    LOCAL_CONFIG_PATH.write_text(f"{json.dumps(config, indent=2)}\n", encoding="utf-8")
    return config


def save_google_oauth_tokens(tokens: dict) -> dict:
    config = load_local_config()
    oauth = get_google_oauth_config()
    oauth["tokens"] = tokens
    config["google_oauth"] = oauth
    LOCAL_CONFIG_PATH.write_text(f"{json.dumps(config, indent=2)}\n", encoding="utf-8")
    return config


def save_google_oauth_state(state: str) -> dict:
    config = load_local_config()
    oauth = get_google_oauth_config()
    oauth["pending_state"] = state
    config["google_oauth"] = oauth
    LOCAL_CONFIG_PATH.write_text(f"{json.dumps(config, indent=2)}\n", encoding="utf-8")
    return config


def clear_google_oauth_tokens() -> dict:
    config = load_local_config()
    oauth = get_google_oauth_config()
    oauth.pop("tokens", None)
    oauth.pop("pending_state", None)
    config["google_oauth"] = oauth
    LOCAL_CONFIG_PATH.write_text(f"{json.dumps(config, indent=2)}\n", encoding="utf-8")
    return config
