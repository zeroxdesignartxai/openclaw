# LyricForge

Creator-grade lyric video studio built with Next.js, Remotion, Tailwind, and Zustand.

## Quickstart

1. Install deps (Node 22+):
   ```bash
   pnpm install
   ```
2. Run dev server:
   ```bash
   pnpm dev
   ```
3. Open http://localhost:3000

## Features
- Upload audio (mp3, wav, m4a)
- Import .txt or .lrc lyrics (timestamp parsing)
- Manual sync timeline with drag + "set from current" controls
- Remotion-powered live preview with karaoke fill
- Five presets (Minimal, Neon, Cinematic, Karaoke, Trap)
- Layouts: centered, bottom subtitle, stacked
- Backgrounds: color, gradient, image/video placeholder
- Typography controls baked into presets
- Exports presets: 16:9, 9:16, 1:1 (mock flow wired for UI)
- Local project save/load; seeded demo song

## Project structure
- `src/app` – Next.js routes (`/`, `/studio`, `/projects`, `/export`)
- `src/components` – UI + editor building blocks (timeline, preview, presets)
- `src/hooks/use-project-store.ts` – Zustand store + local storage
- `src/types/project.ts` – Project schema (lyrics, timing, styles, export)
- `src/data/seedProject.ts` – Demo song and placeholder assets
- `public/demo` – Silent WAV and cover image placeholder

## Lyric timing model
- `LineTiming.start` is seconds from audio start; `end` derived from next line or audio length.
- Word-level timing is optional (`words: WordTiming[]`) for karaoke fill.
- LRC import populates starts; manual sync edits `start` via timeline slider or "set from now" using audio current time.
- Remotion composition finds the active line by comparing current frame time against the next line start; uses 30 fps.

## Adding AI auto-sync (future)
- Use speech-to-text (Whisper or external ASR) to align transcript to audio.
- Map transcript words to timestamps, then merge with provided lyrics using fuzzy matching (e.g., rapidfuzz) to produce `words` arrays.
- If forced alignment is available, replace heuristics with alignment output and set `LineTiming.end` from adjacent word spans.
- Store alignment metadata on the project to avoid recomputation; fall back to manual overrides when confidence is low.

## Deploying fast on Vercel
1. Push this folder to a Git repo.
2. Create a new Vercel project, import the repo, keep `pnpm install` + `pnpm build`.
3. Add `NEXT_TELEMETRY_DISABLED=1` if desired.
4. Set `OUTPUT_DIRECTORY=.next` (default) and ship. Remotion player runs client-side so no extra config required.

## TODO (next steps)
- Wire real Remotion render queue + download (currently mock progress only)
- Add waveform visualization component and album-cover mode toggle in preview
- Add per-word timing editor UI and karaoke fill gradient
- Allow background uploads + video loops (with drag/drop to public storage)
- Add unit tests for LRC parsing and timeline math
- Add auth + cloud project sync (Supabase or NextAuth) when ready
