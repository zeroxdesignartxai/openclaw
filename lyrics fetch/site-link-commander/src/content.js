import { MSG } from './common/messaging.js';
import { injectShadowHost, getActiveEditable, setValue, clickSelector } from './common/dom-utils.js';
import { createFab } from './ui/fab.js';
import { createPanel } from './ui/panel.js';

let shadow;
let ui;
let pairedWith = null;

(async function bootstrap() {
  const allowed = await register();
  if (!allowed) return;
  shadow = injectShadowHost();
  if (!shadow) return; // already injected
  createFab(shadow, togglePanel);
  ui = createPanel(shadow, handlers);
  await refreshPairs();
  await refreshAutomations();
  await refreshLogs();
})();

async function register() {
  const res = await chrome.runtime.sendMessage({ type: MSG.REGISTER, url: location.href });
  if (!res.allowed) return false;
  const perm = await chrome.runtime.sendMessage({ type: MSG.PERMISSION_CHECK, origin: location.origin });
  return perm.granted;
}

function togglePanel() {
  ui.setVisible(ui.panel.hidden);
}

const handlers = {
  async pair(targetId) {
    if (!targetId) return;
    await chrome.runtime.sendMessage({ type: MSG.PAIR, targetTabId: Number(targetId) });
    pairedWith = Number(targetId);
    ui.setPairStatus(`Paired with #${pairedWith}`);
  },
  async unpair() {
    await chrome.runtime.sendMessage({ type: MSG.UNPAIR });
    pairedWith = null;
    ui.setPairStatus('Not paired');
  },
  async action(name) {
    const action = mapAction(name);
    if (!action) return;
    await chrome.runtime.sendMessage({ type: MSG.ACTION, action });
  },
  async saveAutomation(name, rawSteps) {
    if (!name) return;
    let steps;
    try { steps = JSON.parse(rawSteps || '[]'); } catch { return; }
    await chrome.runtime.sendMessage({ type: MSG.AUTOMATION_SAVE, name, steps });
    await refreshAutomations();
  },
  async runAutomation(id) {
    if (!id) return;
    await chrome.runtime.sendMessage({ type: MSG.AUTOMATION_RUN, id });
  },
  async deleteAutomation(id) {
    if (!id) return;
    await chrome.runtime.sendMessage({ type: MSG.AUTOMATION_DELETE, id });
    await refreshAutomations();
  },
  async updateDomain(action) {
    const domain = location.hostname;
    const res = await chrome.runtime.sendMessage({ type: MSG.DOMAIN_UPDATE, domain, action });
    ui.setDomainStatus(`${action}ed ${domain}`);
    return res;
  }
};

function mapAction(name) {
  const selector = ui.getSelector();
  const fillData = ui.getFillData();
  switch (name) {
    case 'send-selection':
      return { type: 'insertText', text: window.getSelection().toString() };
    case 'sync-form': {
      const form = document.querySelector('form');
      if (!form) return null;
      const data = {};
      form.querySelectorAll('input, textarea, select').forEach(el => data[el.name || el.id] = el.value);
      return { type: 'fillForm', data };
    }
    case 'click-selector':
      return selector ? { type: 'click', selector } : null;
    case 'scrape-selector': {
      const el = selector ? document.querySelector(selector) : null;
      return el ? { type: 'insertText', text: el.innerText || el.value || '' } : null;
    }
    case 'fill-form': {
      try {
        const parsed = JSON.parse(fillData || '{}');
        return { type: 'fillForm', data: parsed };
      } catch {
        return null;
      }
    }
    default:
      return null;
  }
}

async function refreshPairs() {
  const res = await chrome.runtime.sendMessage({ type: MSG.REQUEST_PAIR_CANDIDATES });
  ui.setPairs(res.tabs || []);
}

async function refreshAutomations() {
  const res = await chrome.runtime.sendMessage({ type: MSG.AUTOMATION_LIST });
  ui.setAutomations(res.automations || []);
}

async function refreshLogs() {
  const res = await chrome.runtime.sendMessage({ type: MSG.LOG_REQUEST });
  const html = (res.logs || []).slice(0, 20)
    .map(l => `<div>[${new Date(l.ts).toLocaleTimeString()}] ${l.kind} ${l.action ?? ''} ${l.from ?? ''}->${l.to ?? ''}</div>`)
    .join('');
  ui.logs(html);
}

chrome.runtime.onMessage.addListener((msg) => {
  switch (msg.type) {
    case MSG.PAIR:
      pairedWith = msg.from;
      ui.setPairStatus(`Paired with #${pairedWith}`);
      break;
    case MSG.UNPAIR:
      pairedWith = null;
      ui.setPairStatus('Not paired');
      break;
    case MSG.ACTION:
      executeAction(msg.action);
      break;
    case MSG.AUTOMATION_RUN:
      msg.steps.forEach(step => executeAction(step));
      break;
    default:
      break;
  }
});

function executeAction(action) {
  switch (action.type) {
    case 'insertText': {
      const target = getActiveEditable();
      if (!setValue(target, action.text)) {
        navigator.clipboard?.writeText(action.text).catch(() => {});
      }
      break;
    }
    case 'fillForm': {
      const entries = Object.entries(action.data || {});
      entries.forEach(([key, value]) => {
        const el = document.querySelector(`[name="${key}"], #${CSS.escape(key)}`);
        setValue(el, value);
      });
      break;
    }
    case 'click': {
      clickSelector(action.selector);
      break;
    }
    default:
      break;
  }
}
