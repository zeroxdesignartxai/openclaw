// content.js — injected into suno.com pages
// Currently a placeholder; future versions can extract
// in-page auth tokens or observe DOM changes.

// Notify background that we're alive on this tab
chrome.runtime.sendMessage({ action: 'contentReady' }).catch(() => {});
