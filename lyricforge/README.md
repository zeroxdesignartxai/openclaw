# LyricForge Monorepo

Packages:
- `packages/web` – Next.js app (App Router)
- `packages/api` – NestJS service for exports/auth/jobs
- `packages/shared` – Zod schemas and shared types

Scripts (run with pnpm):
- `pnpm dev` (web), `pnpm dev:api` (api), `pnpm build` (both)

Install: `pnpm install` at repo root (uses workspace `packages/*`).
