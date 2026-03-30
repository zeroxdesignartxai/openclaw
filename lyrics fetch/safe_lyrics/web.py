import html
import json
import time
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from safe_lyrics.app_state import (
    create_or_update_user,
    create_session,
    delete_session,
    delete_user_account,
    get_generation_allowance,
    get_user_by_session,
    list_generations,
    record_generation,
    update_user_tier,
)
from safe_lyrics.google_oauth import build_google_auth_url, handle_google_oauth_callback
from safe_lyrics.local_config import (
    clear_provider_api_key,
    get_default_provider,
    get_google_oauth_config,
    get_provider_api_key,
    save_provider_api_key,
    save_google_oauth_settings,
)
from safe_lyrics.service import format_generated_lyrics, generate_safe_lyrics, get_trend_report

SESSION_COOKIE = "lyricmaster_session"

POWER_OPTIONS = [
    ("", "Neutral — balanced, versatile writing"),
    ("Symphonic", "complex, layered systems"),
    ("Indonesian", "region-specific configs"),
    ("Melodic", "readable, maintainable fixes"),
    ("Brutal", "aggressive debugging"),
    ("Technical", "low-level precision"),
    ("Progressive", "forward-looking"),
    ("Slamming", "minimal, fast, direct"),
    ("Blackened", "security-focused"),
    ("Downtempo", "cautious, validated"),
    ("Christian", "safe, ethical"),
    # Spotify-style genre cues
    ("Pop", "hook-forward, radio-ready"),
    ("Dance Pop", "four-on-the-floor energy"),
    ("Indie Pop", "intimate, off-center hooks"),
    ("Rock", "guitar-led drive"),
    ("Alt Rock", "angular, moody edge"),
    ("Indie Rock", "raw texture, storytelling"),
    ("Metal", "high intensity, dramatic stakes"),
    ("Punk", "urgent, concise, defiant"),
    ("Hip-Hop", "rhythmic bars, swagger"),
    ("Trap", "808 bounce, melodic hooks"),
    ("Drill", "sliding 808s, stark imagery"),
    ("R&B", "melodic smoothness"),
    ("Soul", "warm call-and-response"),
    ("Afrobeats", "syncopated celebration"),
    ("Amapiano", "log drum pulse, airy toplines"),
    ("Reggaeton", "dembow swing, playful refrains"),
    ("Latin Pop", "bright bilingual hooks"),
    ("Country", "story-first, concrete places"),
    ("Folk", "narrative intimacy"),
    ("Singer-Songwriter", "lyric-forward, confessional"),
    ("EDM", "build-and-drop tension"),
    ("House", "steady 4/4 groove"),
    ("Techno", "minimal, hypnotic"),
    ("Trance", "uplift, euphoric arcs"),
    ("Drum and Bass", "breakbeat energy"),
    ("K-Pop", "section-switch, chantable"),
    ("J-Pop", "melodic sparkle, crisp diction"),
    ("Jazz", "swung phrasing, rich chords"),
    ("Blues", "call-response grit"),
    ("Classical", "thematic development"),
    ("Lofi", "understated, cozy calm"),
]


def _escape(value: str) -> str:
    return html.escape(value, quote=True)


def _nav_link(path: str, label: str, current_path: str, *, requires_auth: bool = False, is_authenticated: bool = False) -> str:
    if requires_auth and not is_authenticated:
        return ""
    current = "nav-link active" if current_path == path else "nav-link"
    return f'<a href="{path}" class="{current}">{label}</a>'


def _render_layout(*, title: str, body: str, current_path: str, user: dict | None = None, notice: str = "", error: str = "") -> str:
    is_authenticated = user is not None
    user_name = _escape(user.get("name") or user.get("email", "")) if user else ""
    tier = _escape(str(user.get("tier", "free")).upper()) if user else ""
    banner = ""
    if notice:
        banner = f'<div class="banner notice">{_escape(notice)}</div>'
    if error:
        banner += f'<div class="banner error">{_escape(error)}</div>'

    auth_actions = (
        f'<div class="nav-user"><span>{user_name}</span><span class="pill">{tier}</span><a href="/auth/logout" class="nav-link">Log out</a></div>'
        if user
        else '<a href="/auth/google/mock" class="cta ghost">Google Login</a>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{_escape(title)}</title>
    <style>
      :root {{
        --bg: #09090b;
        --surface: rgba(24, 24, 31, 0.92);
        --surface-2: rgba(39, 39, 52, 0.92);
        --border: rgba(161, 161, 170, 0.18);
        --text: #fafafa;
        --muted: #b4b4be;
        --accent: #7c3aed;
        --accent-2: #5b21b6;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        min-height: 100vh;
        color: var(--text);
        font-family: Inter, "Segoe UI", sans-serif;
        background:
          radial-gradient(circle at top left, rgba(124, 58, 237, 0.2), transparent 30%),
          radial-gradient(circle at 90% 10%, rgba(59, 130, 246, 0.18), transparent 28%),
          linear-gradient(180deg, #050507 0%, #09090b 45%, #111118 100%);
      }}
      a {{ color: inherit; text-decoration: none; }}
      button, input, textarea, select {{ font: inherit; }}
      .shell {{ width: min(1320px, calc(100vw - 48px)); margin: 0 auto; padding: 28px 0 56px; }}
      .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 26px; }}
      .brand {{ display: flex; gap: 14px; align-items: center; }}
      .brand-mark {{ width: 42px; height: 42px; border-radius: 14px; background: linear-gradient(135deg, var(--accent), #2563eb); }}
      .brand-copy strong {{ display: block; letter-spacing: 0.04em; }}
      .brand-copy span {{ color: var(--muted); font-size: 0.92rem; }}
      .nav {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
      .nav-link {{ padding: 10px 14px; border-radius: 999px; color: var(--muted); }}
      .nav-link.active, .nav-link:hover {{ color: var(--text); background: rgba(124, 58, 237, 0.16); }}
      .nav-user {{ display: flex; gap: 10px; align-items: center; }}
      .hero, .panel {{ border: 1px solid var(--border); background: var(--surface); border-radius: 28px; box-shadow: 0 28px 80px rgba(0, 0, 0, 0.45); }}
      .hero {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 22px; overflow: hidden; }}
      .hero-copy, .hero-side, .panel {{ padding: 28px; }}
      .eyebrow {{ margin: 0 0 10px; font-size: 0.75rem; letter-spacing: 0.22em; text-transform: uppercase; color: #c4b5fd; }}
      h1, h2, h3, p {{ margin-top: 0; }}
      h1 {{ font-size: clamp(3rem, 6vw, 5rem); line-height: 0.94; margin-bottom: 16px; }}
      .lead, .meta, .support, .empty {{ color: var(--muted); line-height: 1.7; }}
      .cta-row, .button-row, .route-links {{ display: flex; gap: 12px; flex-wrap: wrap; }}
      .cta, button {{ display: inline-flex; align-items: center; justify-content: center; border: 0; cursor: pointer; border-radius: 999px; padding: 13px 18px; font-weight: 700; color: #fff; background: linear-gradient(135deg, var(--accent), var(--accent-2)); }}
      .cta.ghost, .secondary {{ color: var(--text); background: rgba(63, 63, 70, 0.62); }}
      .danger {{ background: linear-gradient(135deg, #e11d48, #be123c); }}
      .grid-3 {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }}
      .metric, .card, .subpanel, .result-box, .list-item {{ padding: 18px; border-radius: 22px; border: 1px solid rgba(161, 161, 170, 0.12); background: var(--surface-2); }}
      .metric strong, .card strong, .list-item strong {{ display: block; margin-bottom: 8px; font-size: 1.15rem; }}
      .banner {{ margin: 0 0 18px; padding: 16px 18px; border-radius: 18px; }}
      .banner.notice {{ background: rgba(52, 211, 153, 0.12); border: 1px solid rgba(52, 211, 153, 0.28); }}
      .banner.error {{ background: rgba(251, 113, 133, 0.12); border: 1px solid rgba(251, 113, 133, 0.28); }}
      .split {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 22px; }}
      .form-grid, .list {{ display: grid; gap: 14px; }}
      label {{ display: grid; gap: 8px; color: var(--muted); font-size: 0.95rem; }}
      input, textarea, select {{ width: 100%; border-radius: 18px; border: 1px solid rgba(161, 161, 170, 0.18); background: rgba(9, 9, 11, 0.96); color: var(--text); padding: 14px 16px; }}
      textarea {{ resize: vertical; min-height: 150px; }}
      .inline-fields {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
      .pill {{ display: inline-flex; align-items: center; justify-content: center; padding: 7px 11px; border-radius: 999px; background: rgba(124, 58, 237, 0.16); color: #ddd6fe; font-size: 0.82rem; }}
      .table {{ width: 100%; border-collapse: collapse; }}
      .table th, .table td {{ padding: 14px 12px; text-align: left; border-bottom: 1px solid rgba(161, 161, 170, 0.1); vertical-align: top; }}
      .table th {{ color: #ddd6fe; font-size: 0.82rem; letter-spacing: 0.12em; text-transform: uppercase; }}
      .lyrics-output {{ white-space: pre-wrap; font-family: "JetBrains Mono", "Courier New", monospace; line-height: 1.8; }}
      @media (max-width: 960px) {{
        .hero, .split, .grid-3, .inline-fields {{ grid-template-columns: 1fr; }}
        .topbar {{ flex-direction: column; align-items: flex-start; }}
      }}
    </style>
  </head>
  <body>
    <main class="shell">
      <header class="topbar">
        <div class="brand">
          <div class="brand-mark"></div>
          <div class="brand-copy">
            <strong>LyricMaster AI</strong>
            <span>Masterpiece Lyrics. Zero Copyright Risk.</span>
          </div>
        </div>
        <nav class="nav">
          {_nav_link("/", "Home", current_path, is_authenticated=is_authenticated)}
          {_nav_link("/dashboard", "Dashboard", current_path, requires_auth=True, is_authenticated=is_authenticated)}
          {_nav_link("/generate", "Generate", current_path, requires_auth=True, is_authenticated=is_authenticated)}
          {_nav_link("/history", "History", current_path, requires_auth=True, is_authenticated=is_authenticated)}
          {_nav_link("/settings", "Settings", current_path, requires_auth=True, is_authenticated=is_authenticated)}
          {auth_actions}
        </nav>
      </header>
      {banner}
      {body}
    </main>
  </body>
</html>"""


def _render_landing_page() -> str:
    body = """
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Desktop SaaS Workspace</p>
        <h1>Masterpiece Lyrics. Zero Copyright Risk.</h1>
        <p class="lead">
          LyricMaster AI builds structurally disciplined, emotionally precise lyrics from abstract style DNA instead of copied lines.
          Every draft passes a consecutive-word originality screen before it is released to the writer.
        </p>
        <div class="cta-row">
          <a href="/auth/google/mock" class="cta">Start Writing for Free</a>
          <a href="#guarantee" class="cta ghost">Read the guarantee</a>
        </div>
        <div class="route-links">
          <span class="pill">Streaming workspace</span>
          <span class="pill">Google sign-in mock</span>
          <span class="pill">5 free generations / month</span>
        </div>
      </div>
      <div class="hero-side">
        <div class="grid-3">
          <div class="metric"><strong>Style DNA</strong><span class="meta">Genre rhythm, imagery, and structure are learned as patterns, not borrowed text.</span></div>
          <div class="metric"><strong>Clash Detection</strong><span class="meta">Any repeated 5-word phrase is blocked and regenerated before the user sees it.</span></div>
          <div class="metric"><strong>Desktop Focus</strong><span class="meta">Dark, distraction-free workflow built for writers under deadline pressure.</span></div>
        </div>
      </div>
    </section>
    """
    return _render_layout(title="LyricMaster AI", body=body, current_path="/")


def _render_login_page(error: str = "") -> str:
    body = """
    <section class="split">
      <section class="panel">
        <p class="eyebrow">Google Authentication</p>
        <h2>Sign in to your writing workspace</h2>
        <p class="lead">This local build uses a deterministic mock Google sign-in so the full product flow can be tested without external OAuth setup.</p>
        <form method="post" action="/auth/google/mock" class="form-grid">
          <label>
            Google account email
            <input type="email" name="email" value="writer@lyricmaster.ai" required>
          </label>
          <label>
            Google user ID
            <input type="text" name="google_id" value="google-writer-001" required>
          </label>
          <label>
            Display name
            <input type="text" name="name" value="Avery Lane" required>
          </label>
          <div class="button-row">
            <button type="submit">Continue with Google</button>
            <a href="/" class="cta ghost">Back</a>
          </div>
        </form>
      </section>
      <section class="panel">
        <p class="eyebrow">What unlocks</p>
        <div class="list">
          <div class="list-item"><strong>Dashboard</strong><p class="meta">Recent drafts, free-tier usage, and quick-start genre cards.</p></div>
          <div class="list-item"><strong>Generate</strong><p class="meta">Streaming lyric output with structure, safety, and provider controls.</p></div>
          <div class="list-item"><strong>History</strong><p class="meta">Saved generations per account, ready for review or reuse.</p></div>
        </div>
      </section>
    </section>
    """
    return _render_layout(title="Google Login", body=body, current_path="/", error=error)


def render_page(
    *,
    values: dict[str, str],
    lyrics: str = "",
    error: str = "",
    originality: dict | None = None,
    trend_summary: dict | None = None,
) -> str:
    result = None
    if lyrics:
        result = {
            "lyrics": lyrics,
            "originality": originality or {},
            "selected_model": values.get("selected_model", "preview"),
        }
    mock_user = {"id": "preview", "name": "Preview Writer", "email": "preview@lyricmaster.ai", "tier": "free"}
    return _render_generate_page(mock_user, values=values, result=result, notice="Preview mode", error=error)


def _render_dashboard_page(user: dict, notice: str = "") -> str:
    allowance = get_generation_allowance(user)
    recent = list_generations(str(user.get("id")))[:3]
    history_html = "".join(
        f"""
        <div class="list-item">
          <strong>{_escape(item.get("genre", "Unknown"))} · {_escape(item.get("mood", ""))}</strong>
          <p class="meta">{_escape(item.get("topic", ""))}</p>
          <span class="pill">{_escape(str(item.get("created_at", ""))[:16].replace("T", " "))}</span>
        </div>
        """
        for item in recent
    ) or '<p class="empty">No generations yet. Start from the generate workspace.</p>'
    remaining = "Unlimited" if allowance["remaining"] is None else str(allowance["remaining"])
    body = f"""
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Writer Workspace</p>
        <h1>{_escape(user.get("name") or "Writer")}, build the next draft fast.</h1>
        <p class="lead">Your workspace is tuned for rapid ideation with strong structure control, plagiarism screening, and saved history.</p>
        <div class="route-links">
          <span class="pill">Tier: {_escape(str(user.get("tier", "free")).upper())}</span>
          <span class="pill">Used this month: {_escape(str(allowance["used"]))}</span>
          <span class="pill">Remaining: {_escape(remaining)}</span>
        </div>
        <div class="cta-row" style="margin-top:18px">
          <a href="/generate" class="cta">Open Generator</a>
          <a href="/settings" class="cta ghost">Manage Plan</a>
        </div>
      </div>
      <div class="hero-side">
        <div class="grid-3">
          <div class="metric"><strong>Synthwave</strong><span class="meta">Neon heartbreak, late-night velocity, memory decay.</span></div>
          <div class="metric"><strong>Pop</strong><span class="meta">Verse-Chorus-Bridge control for radio-ready hooks.</span></div>
          <div class="metric"><strong>Trap</strong><span class="meta">Hook-driven tension, momentum, and hard-edged imagery.</span></div>
        </div>
      </div>
    </section>
    <section class="split">
      <section class="panel">
        <p class="eyebrow">Recent Generations</p>
        <h2>Latest drafts</h2>
        <div class="list">{history_html}</div>
      </section>
      <section class="panel">
        <p class="eyebrow">Quick Start</p>
        <h2>Start from strong defaults</h2>
        <div class="list">
          <div class="list-item"><strong>Pop / Heartbreak</strong><p class="meta">Strict Verse-Chorus-Verse-Chorus-Bridge-Chorus.</p></div>
          <div class="list-item"><strong>Synthwave / Obsession</strong><p class="meta">Neon imagery, cinematic rhythm, retro-future texture.</p></div>
          <div class="list-item"><strong>Country / Homecoming</strong><p class="meta">Concrete place imagery and emotional narrative clarity.</p></div>
        </div>
      </section>
    </section>
    """
    return _render_layout(title="Dashboard", body=body, current_path="/dashboard", user=user, notice=notice)


def _render_generate_page(user: dict, *, values: dict[str, str] | None = None, result: dict | None = None, notice: str = "", error: str = "") -> str:
    values = values or {}
    raw_provider = values.get("provider", get_default_provider())
    provider = _escape(raw_provider)
    api_key = _escape(values.get("api_key", get_provider_api_key(raw_provider)))
    genre = _escape(values.get("genre", "Synthwave"))
    topic = _escape(values.get("topic", "A city drive after a breakup"))
    mood = _escape(values.get("mood", "Cinematic"))
    power = _escape(values.get("power", "Symphonic"))
    allowance = get_generation_allowance(user)
    trend = get_trend_report(values.get("genre", genre))
    output = _escape(result.get("lyrics", "")) if result else ""
    metadata = ""
    if result:
        originality = result.get("originality", {})
        metadata = f"""
        <div class="grid-3" style="margin-bottom:18px">
          <div class="card"><strong>{_escape(str(result.get("selected_model", "n/a")))}</strong><p class="meta">Selected model</p></div>
          <div class="card"><strong>{_escape(str(originality.get("highest_shared_count", 0)))}</strong><p class="meta">Shared 5-grams blocked</p></div>
          <div class="card"><strong>{_escape(str(originality.get("closest_source_id") or "none"))}</strong><p class="meta">Closest source match</p></div>
        </div>
        """
    trend_html = ""
    if trend.get("available"):
        trend_html = f"""
        <div class="card">
          <strong>Trend guidance</strong>
          <p class="meta">Themes: {_escape(", ".join(trend.get("top_themes", [])) or "none")}</p>
          <p class="meta">Moods: {_escape(", ".join(trend.get("top_moods", [])) or "none")}</p>
          <p class="meta">Production: {_escape(", ".join(trend.get("top_production", [])) or "none")}</p>
        </div>
        """
    remaining = "Unlimited" if allowance["remaining"] is None else str(allowance["remaining"])
    disabled = "disabled" if not allowance["allowed"] else ""
    body = f"""
    <section class="split">
      <section class="panel">
        <p class="eyebrow">Generation Engine</p>
        <h2>Compose an original lyric draft</h2>
        <p class="support">Free-tier remaining this month: {_escape(remaining)}</p>
        <form id="generate-form" class="form-grid">
          <div class="inline-fields">
            <label>
              Genre
              <input type="text" name="genre" value="{genre}" required>
            </label>
            <label>
              Mood
              <input type="text" name="mood" value="{mood}" required>
            </label>
          </div>
          <label>
            Beat power
            <select name="power">
              {"".join(
                f'<option value="{_escape(name)}" {"selected" if power == name else ""}>{_escape(name or "Neutral")} — {_escape(desc)}</option>'
                for name, desc in POWER_OPTIONS
              )}
            </select>
          </label>
          <label>
            Topic
            <textarea name="topic" required>{topic}</textarea>
          </label>
          <div class="inline-fields">
            <label>
              Provider
              <select name="provider">
                <option value="openai" {"selected" if provider == "openai" else ""}>OpenAI</option>
                <option value="gemini" {"selected" if provider == "gemini" else ""}>Gemini</option>
              </select>
            </label>
            <label>
              API key
              <input type="password" name="api_key" value="{api_key}" placeholder="Optional saved provider key">
            </label>
          </div>
          <div class="inline-fields">
            <label>
              Draft strategy
              <select name="multi_model">
                <option value="off">Single model</option>
                <option value="on">Multi-model ranking</option>
              </select>
            </label>
            <label>
              Workflow
              <select name="agentic_mode">
                <option value="off">Direct draft</option>
                <option value="on">Plan-critique-revise</option>
              </select>
            </label>
          </div>
          <div class="button-row">
            <button id="generate-button" type="submit" {disabled}>Generate</button>
            <button id="format-button" type="button" class="secondary">Format Output</button>
          </div>
        </form>
      </section>
      <section class="panel">
        <p class="eyebrow">Output Stream</p>
        <h2>Live lyric response</h2>
        {metadata}
        <div id="stream-status" class="pill">Waiting</div>
        <div id="stream-output" class="result-box lyrics-output" style="margin-top:16px">{output or "Streaming output will appear here."}</div>
        {trend_html}
      </section>
    </section>
    <script>
      const form = document.getElementById("generate-form");
      const output = document.getElementById("stream-output");
      const status = document.getElementById("stream-status");
      const formatButton = document.getElementById("format-button");
      async function streamGenerate(payload) {{
        output.textContent = "";
        status.textContent = "Connecting";
        const response = await fetch("/api/v1/generate", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json", "Accept": "text/event-stream" }},
          body: JSON.stringify(payload)
        }});
        if (!response.ok || !response.body) {{
          const errorPayload = await response.json().catch(() => ({{ error: "Generation failed." }}));
          throw new Error(errorPayload.error?.message || errorPayload.error || "Generation failed.");
        }}
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {{
          const {{ value, done }} = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, {{ stream: true }});
          const events = buffer.split("\\n\\n");
          buffer = events.pop() || "";
          for (const rawEvent of events) {{
            const lines = rawEvent.split("\\n");
            let eventName = "message";
            let data = "";
            for (const line of lines) {{
              if (line.startsWith("event:")) eventName = line.slice(6).trim();
              if (line.startsWith("data:")) data += line.slice(5).trim();
            }}
            if (!data) continue;
            const payload = JSON.parse(data);
            if (eventName === "status") status.textContent = payload.message;
            if (eventName === "chunk") output.textContent += payload.text;
            if (eventName === "done") {{
              status.textContent = "Completed";
              if (payload.lyrics) output.textContent = payload.lyrics;
            }}
            if (eventName === "error") {{
              status.textContent = "Failed";
              throw new Error(payload.error || "Generation failed.");
            }}
          }}
        }}
      }}
      form?.addEventListener("submit", async (event) => {{
        event.preventDefault();
        const formData = new FormData(form);
        try {{
          await streamGenerate(Object.fromEntries(formData.entries()));
        }} catch (error) {{
          output.textContent = error.message;
        }}
      }});
      formatButton?.addEventListener("click", async () => {{
        const lyrics = output.textContent.trim();
        if (!lyrics) return;
        const response = await fetch("/api/v1/format", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ lyrics }})
        }});
        const payload = await response.json();
        if (payload.formatted_lyrics) output.textContent = payload.formatted_lyrics;
      }});
    </script>
    """
    return _render_layout(title="Generate", body=body, current_path="/generate", user=user, notice=notice, error=error)


def _render_history_page(user: dict) -> str:
    rows = list_generations(str(user.get("id")))
    table_rows = "".join(
        f"""
        <tr>
          <td>{_escape(str(item.get("created_at", ""))[:16].replace("T", " "))}</td>
          <td>{_escape(item.get("genre", ""))}</td>
          <td>{_escape(item.get("topic", ""))}</td>
          <td>{_escape(item.get("selected_model", ""))}</td>
          <td>{_escape(str(item.get("originality", {}).get("highest_shared_count", 0)))}</td>
        </tr>
        """
        for item in rows
    ) or '<tr><td colspan="5" class="empty">No generations saved yet.</td></tr>'
    body = f"""
    <section class="panel">
      <p class="eyebrow">History</p>
      <h2>Past generations</h2>
      <table class="table">
        <thead>
          <tr><th>Created</th><th>Genre</th><th>Topic</th><th>Model</th><th>Shared 5-grams</th></tr>
        </thead>
        <tbody>{table_rows}</tbody>
      </table>
    </section>
    """
    return _render_layout(title="History", body=body, current_path="/history", user=user)


def _render_settings_page(user: dict, notice: str = "", error: str = "") -> str:
    body = f"""
    <section class="panel">
      <p class="eyebrow">Subscription</p>
      <h2>Plan management</h2>
      <form method="post" action="/settings/subscription" class="form-grid">
        <label>
          Subscription tier
          <select name="tier">
            <option value="free" {"selected" if user.get("tier") == "free" else ""}>Free</option>
            <option value="pro" {"selected" if user.get("tier") == "pro" else ""}>Pro ($15/mo)</option>
          </select>
        </label>
        <button type="submit">Update subscription</button>
      </form>
      <div class="subpanel" style="margin-top:18px">
        <strong>Free tier</strong>
        <p class="meta">5 generations per month with shorter drafts.</p>
        <strong>Pro tier</strong>
        <p class="meta">Unlimited generations and advanced controls.</p>
      </div>
    </section>
    <section class="panel">
      <p class="eyebrow">Privacy</p>
      <h2>Delete account</h2>
      <form method="post" action="/settings/account" class="form-grid">
        <input type="hidden" name="confirm" value="DELETE">
        <button type="submit" class="danger">Delete my account</button>
      </form>
    </section>
    """
    return _render_layout(title="Settings", body=body, current_path="/settings", user=user, notice=notice, error=error)


class LyricsRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        user = self._current_user()
        try:
            if parsed.path == "/api/health":
                self._send_json({"ok": True, "status": "healthy"})
                return
            if parsed.path == "/api/trends":
                query = parse_qs(parsed.query, keep_blank_values=True)
                self._send_json(get_trend_report(query.get("genre", [""])[0]))
                return
            if parsed.path == "/api/v1/users/me":
                if not user:
                    self._send_json({"error": {"code": "UNAUTHORIZED", "message": "Authentication required."}}, status=401)
                    return
                self._send_json({"user": user, "allowance": get_generation_allowance(user)})
                return
            if parsed.path == "/api/v1/history":
                if not user:
                    self._send_json({"error": {"code": "UNAUTHORIZED", "message": "Authentication required."}}, status=401)
                    return
                self._send_json({"items": list_generations(str(user.get("id")))})
                return
            if parsed.path == "/oauth/google/callback":
                self._handle_google_oauth_callback(parsed)
                return
            if parsed.path == "/auth/google/mock":
                self._send_html(_render_login_page())
                return
            if parsed.path == "/auth/logout":
                self._clear_session_cookie()
                return
            if parsed.path == "/":
                self._send_html(_render_landing_page())
                return
            if parsed.path == "/dashboard":
                self._require_auth(user)
                self._send_html(_render_dashboard_page(user))
                return
            if parsed.path == "/generate":
                self._require_auth(user)
                self._send_html(_render_generate_page(user))
                return
            if parsed.path == "/history":
                self._require_auth(user)
                self._send_html(_render_history_page(user))
                return
            if parsed.path == "/settings":
                self._require_auth(user)
                self._send_html(_render_settings_page(user))
                return
            self.send_response(404)
            self.end_headers()
        except RuntimeError as error:
            if str(error) != "redirect":
                raise

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        user = self._current_user()
        try:
            if parsed.path == "/api/v1/auth/google":
                self._handle_api_google_auth()
                return
            if parsed.path in {"/api/v1/generate", "/api/generate"}:
                self._handle_api_generate(user, stream=parsed.path == "/api/v1/generate")
                return
            if parsed.path in {"/api/v1/format", "/api/format"}:
                self._handle_api_format()
                return
            if parsed.path == "/auth/google/mock":
                self._handle_google_login()
                return
            if parsed.path == "/settings":
                self._require_auth(user)
                self._handle_settings(user)
                return
            if parsed.path == "/settings/google-oauth":
                self._require_auth(user)
                self._handle_google_oauth_settings(user)
                return
            if parsed.path == "/settings/subscription":
                self._require_auth(user)
                self._handle_subscription_settings(user)
                return
            if parsed.path == "/settings/account":
                self._require_auth(user)
                self._handle_account_delete(user)
                return
            self.send_response(404)
            self.end_headers()
        except RuntimeError as error:
            if str(error) != "redirect":
                raise

    def log_message(self, format: str, *args) -> None:
        return

    def _current_user(self) -> dict | None:
        cookie_header = self.headers.get("Cookie", "")
        if not cookie_header:
            return None
        jar = cookies.SimpleCookie()
        jar.load(cookie_header)
        token = jar.get(SESSION_COOKIE)
        if not token:
            return None
        return get_user_by_session(token.value)

    def _require_auth(self, user: dict | None) -> None:
        if user is None:
            self.send_response(302)
            self.send_header("Location", "/auth/google/mock")
            self.end_headers()
            raise RuntimeError("redirect")

    def _send_html(self, page: str, *, status: int = 200) -> None:
        data = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _set_session_cookie(self, token: str) -> None:
        self.send_response(302)
        self.send_header("Location", "/dashboard")
        self.send_header("Set-Cookie", f"{SESSION_COOKIE}={token}; HttpOnly; Path=/; SameSite=Lax")
        self.end_headers()

    def _clear_session_cookie(self) -> None:
        cookie_header = self.headers.get("Cookie", "")
        if cookie_header:
            jar = cookies.SimpleCookie()
            jar.load(cookie_header)
            token = jar.get(SESSION_COOKIE)
            if token:
                delete_session(token.value)
        self.send_response(302)
        self.send_header("Location", "/")
        self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; HttpOnly; Path=/; Max-Age=0; SameSite=Lax")
        self.end_headers()

    def _read_body(self) -> str:
        content_length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(content_length).decode("utf-8")

    def _read_json_body(self) -> dict:
        body = self._read_body()
        if not body.strip():
            return {}
        return json.loads(body)

    def _read_form_body(self) -> dict[str, str]:
        form = parse_qs(self._read_body(), keep_blank_values=True)
        return {key: values[0] if values else "" for key, values in form.items()}

    def _handle_google_login(self) -> None:
        form = self._read_form_body()
        try:
            user = create_or_update_user(
                email=form.get("email", ""),
                google_id=form.get("google_id", ""),
                name=form.get("name", ""),
            )
        except RuntimeError as error:
            self._send_html(_render_login_page(str(error)))
            return
        token = create_session(str(user.get("id")))
        self._set_session_cookie(token)

    def _handle_api_google_auth(self) -> None:
        try:
            payload = self._read_json_body()
            user = create_or_update_user(
                email=str(payload.get("email", "")),
                google_id=str(payload.get("google_id", "")),
                name=str(payload.get("name", "")),
            )
            token = create_session(str(user.get("id")))
            self._send_json({"user": user, "session_token": token})
        except Exception as error:
            self._send_json({"error": {"code": "AUTH_FAILED", "message": str(error)}}, status=400)

    def _emit_sse(self, *, event: str, payload: dict) -> None:
        self.wfile.write(f"event: {event}\ndata: {json.dumps(payload)}\n\n".encode("utf-8"))
        self.wfile.flush()

    def _handle_api_generate(self, user: dict | None, *, stream: bool) -> None:
        if not user:
            self._send_json({"error": {"code": "UNAUTHORIZED", "message": "Authentication required."}}, status=401)
            return
        try:
            payload = self._read_json_body()
            allowance = get_generation_allowance(user)
            if not allowance["allowed"]:
                self._send_json(
                    {"error": {"code": "UPGRADE_REQUIRED", "message": "Free tier limit reached. Upgrade to Pro to continue."}},
                    status=403,
                )
                return
            if stream:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True
                self._emit_sse(event="status", payload={"message": "Generating"})
            result = generate_safe_lyrics(
                genre=str(payload.get("genre", "")),
                topic=str(payload.get("topic", "")),
                mood=str(payload.get("mood", "")),
                power=str(payload.get("power", "")),
                provider=str(payload.get("provider", "openai")),
                api_key=str(payload.get("api_key", "")),
                multi_model=str(payload.get("multi_model", "")).lower() in {"true", "1", "on"},
                agentic_mode=str(payload.get("agentic_mode", "")).lower() in {"true", "1", "on"},
            )
            saved = record_generation(
                user_id=str(user.get("id")),
                genre=str(payload.get("genre", "")),
                topic=str(payload.get("topic", "")),
                mood=str(payload.get("mood", "")),
                power=str(payload.get("power", "")),
                lyrics=result["lyrics"],
                provider=result["provider"],
                selected_model=str(result.get("selected_model", "")),
                originality=result["originality"],
            )
            result["generation_id"] = saved["id"]
            if stream:
                self._emit_sse(event="status", payload={"message": "Screening"})
                for line in result["lyrics"].splitlines(keepends=True):
                    self._emit_sse(event="chunk", payload={"text": line})
                    time.sleep(0.01)
                self._emit_sse(event="done", payload=result)
                return
            self._send_json(result)
        except Exception as error:
            if stream:
                self._emit_sse(event="error", payload={"error": str(error)})
                return
            self._send_json({"error": str(error)}, status=400)

    def _handle_api_format(self) -> None:
        try:
            payload = self._read_json_body()
            self._send_json(format_generated_lyrics(str(payload.get("lyrics", ""))))
        except Exception as error:
            self._send_json({"error": str(error)}, status=400)

    def _handle_settings(self, user: dict) -> None:
        form = self._read_form_body()
        provider = form.get("provider", "openai")
        api_key = form.get("api_key", "")
        action = form.get("settings_action", "save")
        if action == "clear":
            clear_provider_api_key(provider)
            self._send_html(_render_settings_page(user, notice=f"Cleared saved key for {provider}."))
            return
        save_provider_api_key(provider, api_key)
        self._send_html(_render_settings_page(user, notice=f"Saved local key for {provider}."))

    def _handle_google_oauth_settings(self, user: dict) -> None:
        form = self._read_form_body()
        save_google_oauth_settings(
            form.get("google_client_id", ""),
            form.get("google_client_secret", ""),
            form.get("google_project_id", ""),
        )
        if form.get("oauth_action", "save") == "connect":
            try:
                self.send_response(302)
                self.send_header("Location", build_google_auth_url())
                self.end_headers()
            except Exception as error:
                self._send_html(_render_settings_page(user, error=str(error)))
            return
        self._send_html(_render_settings_page(user, notice="Saved Google OAuth settings."))

    def _handle_google_oauth_callback(self, parsed_url) -> None:
        query = parse_qs(parsed_url.query, keep_blank_values=True)
        if "error" in query:
            self._send_html(_render_login_page(f"Google OAuth failed: {query['error'][0]}"))
            return
        try:
            handle_google_oauth_callback(query.get("code", [""])[0], query.get("state", [""])[0])
            self._send_html(_render_login_page("Provider OAuth connected. You can now use Gemini without pasting an API key."))
        except Exception as error:
            self._send_html(_render_login_page(str(error)))

    def _handle_subscription_settings(self, user: dict) -> None:
        form = self._read_form_body()
        try:
            updated = update_user_tier(str(user.get("id")), form.get("tier", "free"))
            self._send_html(_render_settings_page(updated, notice=f"Subscription updated to {updated['tier'].upper()}."))
        except Exception as error:
            self._send_html(_render_settings_page(user, error=str(error)))

    def _handle_account_delete(self, user: dict) -> None:
        form = self._read_form_body()
        if form.get("confirm") != "DELETE":
            self._send_html(_render_settings_page(user, error="Account deletion confirmation failed."))
            return
        delete_user_account(str(user.get("id")))
        self._clear_session_cookie()


def run_server(host: str = "127.0.0.1", port: int = 8000) -> int:
    server = ThreadingHTTPServer((host, port), LyricsRequestHandler)
    print(f"LyricMaster AI running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
