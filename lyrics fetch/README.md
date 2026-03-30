# Direct Answer Engine — Monorepo Skeleton

This repo scaffolds the **Direct Answer Engine**: a full-stack app that returns a single best answer without exposing internal reasoning. It includes a Next.js frontend, a FastAPI backend, PostgreSQL schema, and Redis cache hooks.

## Structure
- `apps/web` – Next.js 15 UI (query input, result page, admin console)
- `apps/api` – FastAPI backend (parser, router, scorer, formatter, hidden tokenize-to-cluster pipeline)
- `packages/shared` – shared types/constants
- `docker-compose.yml` – local Postgres, Redis, API, and Web

## Quick start (local, dev)
```bash
# backend
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend (separate terminal)
cd apps/web
npm install
npm run dev
```

### Docker compose
```bash
docker-compose up --build
```

## Environment
- Postgres URL: `DATABASE_URL=postgresql://dae:dae@localhost:5432/dae`
- Redis URL: `REDIS_URL=redis://localhost:6379/0`
- Backend: `API_HOST=http://localhost:8000`
- Frontend: `NEXT_PUBLIC_API_BASE=http://localhost:8000`

## MVP checklist
- Submit query ➜ receive top answer
- Category routing and scoring wired
- Hidden tokenize-to-cluster pipeline runs when user data provided
- Admin can edit category rules
- UI never shows reasoning/trace

## Next steps after MVP
- User accounts, saved searches, A/B answer formatting, affiliate links, analytics, per-category tuning.
