import json
import os
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_FALLBACK_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
)


def generate_lyrics(
    prompt: str,
    provider: str = "openai",
    api_key: str | None = None,
    model: str | None = None,
    oauth_token: str | None = None,
    google_project_id: str | None = None,
) -> str:
    normalized_provider = provider.strip().lower()
    if normalized_provider == "gemini":
        return _generate_gemini_lyrics(
            prompt,
            api_key=api_key,
            model=model,
            oauth_token=oauth_token,
            google_project_id=google_project_id,
        )
    if normalized_provider == "openai":
        return _generate_openai_lyrics(prompt, api_key=api_key, model=model)
    raise RuntimeError(f"Unsupported provider: {provider}")


def _generate_openai_lyrics(prompt: str, api_key: str | None = None, model: str | None = None) -> str:
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OpenAI API key is required.")

    base_url = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)
    model = model or os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    payload = json.dumps({"model": model, "input": prompt}).encode("utf-8")

    request = urllib.request.Request(
        f"{base_url}/responses",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI request failed: {error.code} {body}") from error

    text = data.get("output_text", "").strip()
    if not text:
        raise RuntimeError("Model returned an empty response.")
    return text


def _generate_gemini_lyrics(
    prompt: str,
    api_key: str | None = None,
    model: str | None = None,
    oauth_token: str | None = None,
    google_project_id: str | None = None,
) -> str:
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key and not oauth_token:
        raise RuntimeError("Gemini API key or Google OAuth connection is required.")

    base_url = os.environ.get("GEMINI_BASE_URL", DEFAULT_GEMINI_BASE_URL)
    payload = json.dumps(
        {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ]
        }
    ).encode("utf-8")

    configured_model = model or os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    candidate_models = [configured_model, *[model for model in GEMINI_FALLBACK_MODELS if model != configured_model]]
    last_error = None

    for model in candidate_models:
        url = f"{base_url}/models/{model}:generateContent"
        headers = {"Content-Type": "application/json"}
        if oauth_token:
            headers["Authorization"] = f"Bearer {oauth_token}"
            if google_project_id:
                headers["x-goog-user-project"] = google_project_id
        else:
            url = f"{url}?key={api_key}"

        request = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            last_error = (model, error.code, body)
            if error.code == 404:
                continue
            raise RuntimeError(f"Gemini request failed for model {model}: {error.code} {body}") from error
    else:
        model, code, body = last_error if last_error else ("unknown", "unknown", "unknown error")
        raise RuntimeError(f"Gemini request failed for model {model}: {code} {body}")

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text
