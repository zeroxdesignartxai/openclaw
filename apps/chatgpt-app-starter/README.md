# ChatGPT App Starter

This starter adapts the current OpenAI Apps SDK quickstart into an isolated repo shape that is easy to run locally and easy to replace with your own tools.

## Archetype

`vanilla-widget`

This is the smallest useful shape when you want a working MCP server plus an in-ChatGPT widget without pulling in a React toolchain.

## Upstream Basis

- Official quickstart todo app
- Current Apps SDK server and UI guidance

## Repo Shape

```text
apps/chatgpt-app-starter/
├─ package.json
├─ tsconfig.json
├─ public/
│  └─ todo-widget.html
└─ src/
   └─ server.ts
```

## Tools

- `list_todos`
  Use this when the user wants the current todo list without changing anything.
- `add_todo`
  Use this when the user wants to create a new todo item.
- `complete_todo`
  Use this when the user wants to mark an existing todo item as done.

This starter is not connector-like, so it keeps app-specific tools. If you adapt it into a knowledge source, sync app, or connector-style integration, replace read-only discovery with the standard `search` and `fetch` tools and match the official schemas exactly.

## Local Run

```bash
cd apps/chatgpt-app-starter
pnpm install
pnpm dev
```

The server listens on `http://localhost:8787/mcp`.

## ChatGPT Developer Mode

1. Expose the local server over HTTPS, for example `ngrok http 8787`.
2. In ChatGPT, enable Developer Mode under `Settings -> Apps & Connectors -> Advanced settings`.
3. Create a new app using the tunneled `https://.../mcp` URL.
4. Refresh the app in ChatGPT after changing tool metadata or resource URIs.

## Validation

Validation depends on local dependency install. This scaffold is designed to support:

- `pnpm check` for TypeScript validation
- local startup with `pnpm dev`
- MCP Inspector against `http://localhost:8787/mcp`

If you evolve this into a production or submission-ready app, add deployment-specific `_meta.ui.domain`, tighten `_meta.ui.csp`, and validate the hosted endpoint in ChatGPT before submission.
