export const KEYS = {
  PAIRINGS: 'pairings',
  DOMAINS: 'domains',
  AUTOMATIONS: 'automations',
  LOGS: 'logs'
};

export async function get(key, fallback) {
  const data = await chrome.storage.local.get(key);
  return data[key] ?? fallback;
}

export async function set(key, value) {
  return chrome.storage.local.set({ [key]: value });
}

export async function pushLog(entry) {
  const logs = await get(KEYS.LOGS, []);
  logs.unshift({ ts: Date.now(), ...entry });
  return set(KEYS.LOGS, logs.slice(0, 500));
}
