# AGENTS

Goal: "Build a premium lyric video studio where creators can import audio + lyrics, sync timings, preview, and export 16:9 / 9:16 / 1:1 videos."

Context
- Stack: Next.js (App Router), TypeScript, Tailwind, shadcn-style primitives, Zustand, Remotion player, React Hook Form (available), Zod (available).
- State: `use-project-store` (Zustand) holds `Project` schema in `src/types/project.ts` with theme + export settings.
- Demo assets: `public/demo` holds silent WAV + cover placeholder; `src/data/seedProject.ts` auto-loads demo project.
- Routes: `/` landing, `/studio` editor, `/projects` local saves, `/export` export UI (mock progress).
- UI palette: defined in `tailwind.config.js`, glassmorphism + neon gradients; keep mobile-friendly layouts.

Inputs
- Audio: mp3/wav/m4a (file input -> object URL), optional duration read from metadata.
- Lyrics: paste or upload .txt/.lrc; `.lrc` parsed via `parse-lrc.ts`.

Outputs
- Live Remotion preview in `PreviewCanvas` using `LyricComposition`.
- Export presets (UI only) show 1080p, vertical, square; render progress is mocked.

Constraints
- Do not add new dependencies without need; follow Tailwind + shadcn patterns already in `components/ui`.
- Keep components under 200 LOC when possible; prefer extracting helpers.
- No database; persistence is browser localStorage via `upsertProjectToLocal` / `loadFromLocal`.
- Keep imports within `src` (path alias `@/*`).
- Avoid disabling TypeScript strictness; no `any`/`@ts-nocheck`.

Edge cases to cover
- Missing audio: preview renders background + text only.
- LRC lines without timestamps: ignore those lines.
- Clipboard paste with blank lines: trimmed out.
- Local storage parse errors: catch and log, avoid crash.

Output format
- Default responses: concise diffs or file paths. When committing, use `scripts/committer`.

Examples
- See `src/components/editor/timeline.tsx` for manual sync pattern and slider controls.
- See `src/components/editor/remotion-composition.tsx` for how active line is selected per frame.
