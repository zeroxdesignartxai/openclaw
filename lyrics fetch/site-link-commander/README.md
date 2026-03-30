# SiteLink Commander (Chrome MV3)

Pair two tabs, create command links, and run reusable workflows (transfer text, sync forms, click elements, scrape and fill) via a floating edge button.

## Setup
1. Open `chrome://extensions`.
2. Enable **Developer mode** (top right).
3. Click **Load unpacked** and select the `site-link-commander` folder.
4. When a site first loads, the extension will request host permission for that domain; click **Allow** so the UI appears.

## Usage
- On allowed pages, the floating ⇆ button appears at the right edge. Click to open the panel.
- **Pair**: choose another tab in the dropdown → **Pair**. Unpair anytime.
- **Actions**: send selection, sync current form, click CSS selector, scrape selector, fill form with JSON.
- **Automations**: paste an array of steps (e.g., `[{"type":"sendSelection"},{"type":"click","selector":"button.submit"}]`), save, run, or delete. Steps relay to the paired tab.
- **Domain controls**: allow/block the current domain (block hides the UI).
- **Logs**: recent actions are shown at the bottom; stored locally.

## Architecture
- `manifest.json` — MV3 manifest.
- `src/background.js` — pairing state, automations, logging, domain allow/block, message routing.
- `src/content.js` — UI injection, permission gating, action capture, automation execution.
- `src/common/*` — shared storage and messaging helpers.
- `src/ui/*` — floating button, panel, and styles (no external deps).

## Extending
- Add new actions in `mapAction` (sender) and `executeAction` (receiver).
- Adjust log retention in `pushLog` (storage).
- Add more panel controls in `src/ui/panel.js`.
