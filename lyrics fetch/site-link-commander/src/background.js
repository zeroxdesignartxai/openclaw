import { KEYS, get, set, pushLog } from './common/storage.js';
import { MSG } from './common/messaging.js';

const defaultDomains = { allow: [], block: [] };

chrome.runtime.onInstalled.addListener(async () => {
  const domains = await get(KEYS.DOMAINS, null);
  if (!domains) await set(KEYS.DOMAINS, defaultDomains);
  await set(KEYS.PAIRINGS, {});
  await set(KEYS.AUTOMATIONS, []);
  await set(KEYS.LOGS, []);
});

chrome.tabs.onRemoved.addListener(async (tabId) => {
  const pairings = await get(KEYS.PAIRINGS, {});
  Object.keys(pairings).forEach(id => {
    if (+id === tabId || pairings[id] === tabId) delete pairings[id];
  });
  await set(KEYS.PAIRINGS, pairings);
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    switch (msg.type) {
      case MSG.REGISTER: {
        const domains = await get(KEYS.DOMAINS, defaultDomains);
        const domain = new URL(msg.url).hostname;
        const blocked = domains.block.includes(domain);
        const allowed = domains.allow.length === 0 || domains.allow.includes(domain);
        sendResponse({ allowed: allowed && !blocked, domains });
        break;
      }
      case MSG.REQUEST_PAIR_CANDIDATES: {
        const tabs = await chrome.tabs.query({ active: false, currentWindow: true });
        sendResponse({ tabs: tabs.map(t => ({ id: t.id, title: t.title ?? t.url })) });
        break;
      }
      case MSG.PERMISSION_CHECK: {
        const origin = msg.origin;
        chrome.permissions.contains({ origins: [`${origin}/*`] }, (has) => {
          if (has) return sendResponse({ granted: true });
          chrome.permissions.request({ origins: [`${origin}/*`] }, (granted) => sendResponse({ granted }));
        });
        break;
      }
      case MSG.PAIR: {
        const { targetTabId } = msg;
        const src = sender.tab.id;
        const pairings = await get(KEYS.PAIRINGS, {});
        pairings[src] = targetTabId;
        pairings[targetTabId] = src;
        await set(KEYS.PAIRINGS, pairings);
        await pushLog({ kind: 'pair', src, target: targetTabId });
        chrome.tabs.sendMessage(targetTabId, { type: MSG.PAIR, from: src });
        sendResponse({ ok: true });
        break;
      }
      case MSG.UNPAIR: {
        const src = sender.tab.id;
        const pairings = await get(KEYS.PAIRINGS, {});
        const other = pairings[src];
        delete pairings[src];
        if (other) delete pairings[other];
        await set(KEYS.PAIRINGS, pairings);
        await pushLog({ kind: 'unpair', src, target: other });
        if (other) chrome.tabs.sendMessage(other, { type: MSG.UNPAIR, from: src });
        sendResponse({ ok: true });
        break;
      }
      case MSG.ACTION: {
        const pairings = await get(KEYS.PAIRINGS, {});
        const target = pairings[sender.tab.id];
        if (target) {
          chrome.tabs.sendMessage(target, { type: MSG.ACTION, action: msg.action, from: sender.tab.id });
          await pushLog({ kind: 'action', action: msg.action.type, from: sender.tab.id, to: target });
        }
        sendResponse({ ok: Boolean(target) });
        break;
      }
      case MSG.AUTOMATION_SAVE: {
        const list = await get(KEYS.AUTOMATIONS, []);
        const id = crypto.randomUUID();
        list.push({ id, name: msg.name, steps: msg.steps });
        await set(KEYS.AUTOMATIONS, list);
        sendResponse({ id });
        break;
      }
      case MSG.AUTOMATION_LIST: {
        sendResponse({ automations: await get(KEYS.AUTOMATIONS, []) });
        break;
      }
      case MSG.AUTOMATION_DELETE: {
        const list = await get(KEYS.AUTOMATIONS, []);
        await set(KEYS.AUTOMATIONS, list.filter(a => a.id !== msg.id));
        sendResponse({ ok: true });
        break;
      }
      case MSG.AUTOMATION_RUN: {
        const list = await get(KEYS.AUTOMATIONS, []);
        const auto = list.find(a => a.id === msg.id);
        if (auto) {
          const pairings = await get(KEYS.PAIRINGS, {});
          const target = pairings[sender.tab.id];
          if (target) {
            chrome.tabs.sendMessage(target, { type: MSG.AUTOMATION_RUN, steps: auto.steps, from: sender.tab.id });
            await pushLog({ kind: 'automation', id: auto.id, from: sender.tab.id, to: target });
          }
        }
        sendResponse({ ok: Boolean(auto) });
        break;
      }
      case MSG.DOMAIN_UPDATE: {
        const domains = await get(KEYS.DOMAINS, defaultDomains);
        const host = msg.domain;
        if (msg.action === 'allow') {
          domains.block = domains.block.filter(d => d !== host);
          if (!domains.allow.includes(host)) domains.allow.push(host);
        } else if (msg.action === 'block') {
          domains.allow = domains.allow.filter(d => d !== host);
          if (!domains.block.includes(host)) domains.block.push(host);
        }
        await set(KEYS.DOMAINS, domains);
        sendResponse({ domains });
        break;
      }
      case MSG.LOG_REQUEST: {
        sendResponse({ logs: await get(KEYS.LOGS, []) });
        break;
      }
      default:
        break;
    }
  })();
  return true;
});
