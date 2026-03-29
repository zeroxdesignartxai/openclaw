# generate-lyrics-ai

One-day MVP scaffold for an AI lyric music video generator:

- Upload MP3/MP4 or paste a YouTube URL.
- Whisper transcription + timestamps → SRT + JSON.
- FFmpeg renders lyric-highlighted video (16:9 and 9:16) with gradient/cover-blur/VHS themes.
- Optional SDXL-generated scene frames (toggle off by default); caching by audio hash + section.
- Guardrails: 4-minute cap, per-user daily cap, watermark for free runs, hash-based dedupe, retry-safe job IDs.

## Project layout

- `web/` — Next.js 15 app (App Router) for upload, job status, downloads.
- `worker/` — Node worker (Fly VM friendly) for transcription, image gen, and rendering.
- `supabase/` — SQL schema migrations (users, jobs, frames) and storage buckets.
- `docs/` — ADRs and runbooks.

## Day-one milestones (compressed from 4-week plan)
1. Scaffold web app, Supabase auth/storage, job creation, status polling, signed uploads, enqueue jobs.
2. Worker: audio hash → Whisper.cpp transcription → SRT/JSON → FFmpeg text-only render (gradient, 16:9 + 9:16) → upload outputs.
3. Add themes (cover-blur, VHS), dedupe + caps + watermark.
4. Optional SDXL frames with caching; fall back to text-only on failure.
5. Polished UX: progress states, download links, cost/cap hints, basic metrics (job durations, failures).

## Quick start (after deps are installed)
- `cd web && pnpm dev` — run Next.js locally.
- `cd worker && pnpm dev` — run worker loop locally (expects env + Supabase).

## Environment
Copy `.env.example` to both `web/.env.local` and `worker/.env` and fill in:
```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_STORAGE_BUCKET=lyrics-audio
REDIS_URL=          # Upstash or compatible
REPLICATE_API_TOKEN= # optional SDXL
```
