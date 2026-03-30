// ============================================================
// Suno Pro Downloader — Popup Script
// ============================================================

// ── Helpers ─────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const PAGE_SIZES = { '10': 10, '20': 20, '50': 50 };

function showScreen(name) {
  ['loading', 'locked', 'app'].forEach(s =>
    $(`screen-${s}`).classList.toggle('hidden', s !== name)
  );
}

let toastTimer;
function toast(msg, type = 'info') {
  const el = document.getElementById('toast') || createToast();
  el.textContent = msg;
  el.className   = `show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 2800);
}
function createToast() {
  const el = document.createElement('div');
  el.id = 'toast';
  document.body.appendChild(el);
  return el;
}

function sendBg(action, extra = {}) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ action, ...extra }, res => {
      if (chrome.runtime.lastError)
        return reject(new Error(chrome.runtime.lastError.message));
      if (!res || !res.ok)
        return reject(new Error(res?.error || 'Unknown error'));
      resolve(res.data);
    });
  });
}

// ── State ────────────────────────────────────────────────────
let state = {
  page:       0,
  pageSize:   20,
  songs:      [],
  playlists:  [],
  selected:   new Set(),
  totalSongs: 0,
  searchQ:    '',
  playlistId: '',
  format:     'mp3',
  loading:    false,
  formats:    new Set(['mp3'])
};

// ── Boot ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadSettings();
  showScreen('loading');
  doAuthCheck();
  wireEvents();
});

// ── Auth check ───────────────────────────────────────────────
async function doAuthCheck() {
  try {
    const auth = await sendBg('checkAuth');

    if (!auth.isPremium) {
      // Show locked screen
      $('lock-title').textContent    = auth.username
        ? `Hey ${auth.username} 👋` : 'Premium Only';
      $('lock-message').textContent  =
        'This extension is exclusively for Suno Pro & Premier subscribers. '
        + 'Your current plan does not include download access.';
      const badge = $('lock-tier-badge');
      badge.textContent  = (auth.tier || 'free').toUpperCase() + ' PLAN';
      badge.className    = `tier-badge tier-${(auth.tier || 'free').toLowerCase()}`;
      showScreen('locked');
      return;
    }

    // Populate header
    $('user-name').textContent = auth.username || 'Suno User';
    $('user-tier').textContent = (auth.tier || 'pro').toUpperCase();
    if (auth.avatarUrl) $('user-avatar').src = auth.avatarUrl;

    // Update pro badge label for premier
    if ((auth.tier || '').toLowerCase() === 'premier') {
      document.querySelector('.pro-badge').innerHTML =
        '★ PREMIER';
    }

    showScreen('app');
    await loadPlaylists();
    await loadSongs();
    await refreshQueue();

  } catch (err) {
    // If error is not-logged-in, show locked
    const msg = err.message || '';
    if (msg.includes('NOT_LOGGED_IN') || msg.includes('No active session')) {
      $('lock-title').textContent   = 'Not Logged In';
      $('lock-message').textContent =
        'Open app.suno.ai in a normal tab, log in, then reopen the extension. If in Incognito, enable “Allow in incognito” and allow third-party cookies for Suno.';
      $('lock-tier-badge').className   = 'tier-badge tier-free';
      $('lock-tier-badge').textContent = 'NOT LOGGED IN';
    } else if (msg.includes('CLERK_CLIENT_FAILED') || msg.includes('CLERK_TOKEN_FAILED')) {
      $('lock-title').textContent   = 'Suno Auth Blocked';
      $('lock-message').textContent =
        'Could not read Suno session cookies. Make sure you are logged in at app.suno.ai and that cookies are allowed (turn off blockers for Suno).';
      $('lock-tier-badge').className   = 'tier-badge tier-free';
      $('lock-tier-badge').textContent = 'COOKIE BLOCKED';
    } else {
      $('lock-title').textContent   = 'Connection Error';
      $('lock-message').textContent =
        'Could not verify your subscription. Make sure you\'re on suno.com and try again.';
    }
    showScreen('locked');
  }
}

// ── Playlist loader ─────────────────────────────────────────
async function loadPlaylists() {
  try {
    const data = await sendBg('fetchPlaylists');
    const items = data.playlists || data.data || data || [];
    state.playlists = items;

    const sel  = $('lib-playlist');
    // clear existing except first option
    while (sel.options.length > 1) sel.remove(1);

    items.forEach(pl => {
      const opt = document.createElement('option');
      opt.value       = pl.id;
      opt.textContent = pl.name || pl.title || pl.id;
      sel.appendChild(opt);
    });
  } catch {
    // Non-fatal — playlists just won't be available
  }
}

// ── Song loader ─────────────────────────────────────────────
async function loadSongs() {
  if (state.loading) return;
  state.loading = true;

  $('song-list').innerHTML =
    '<div class="list-loading"><div class="spinner-ring small"></div><span>Loading…</span></div>';

  try {
    const data = await sendBg('fetchSongs', {
      params: {
        page:       state.page,
        pageSize:   state.pageSize,
        playlistId: state.playlistId || null
      }
    });

    let songs = data.clips || data.data || data.songs || data || [];

    // Client-side search filter
    if (state.searchQ) {
      const q = state.searchQ.toLowerCase();
      songs = songs.filter(s =>
        (s.title || '').toLowerCase().includes(q) ||
        (s.metadata?.tags || '').toLowerCase().includes(q)
      );
    }

    state.songs     = songs;
    state.totalSongs = data.total_count ?? data.total ?? songs.length;
    state.selected.clear();

    renderSongs();
    updateBulkBar();
    updatePagination();

  } catch (err) {
    $('song-list').innerHTML = `
      <div class="empty-state">
        <p>Failed to load songs</p>
        <span>${err.message}</span>
      </div>`;
  } finally {
    state.loading = false;
  }
}

// ── Manual Auth Display ──────────────────────────────────────
function updateManualAuthUI() {
  chrome.storage.local.get(['manualCookie'], (data) => {
    $('input-manual-cookie').value = data.manualCookie || '';
    $('btn-clear-manual').classList.toggle('hidden', !data.manualCookie);
  });
}

// ── Render songs ─────────────────────────────────────────────
function renderSongs() {
  const list = $('song-list');

  if (!state.songs.length) {
    list.innerHTML = `
      <div class="empty-state">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
        </svg>
        <p>No songs found</p>
        <span>Try a different search or playlist.</span>
      </div>`;
    return;
  }

  list.innerHTML = '';
  state.songs.forEach(song => {
    const isSelected = state.selected.has(song.id);
    const thumb      = song.image_url || song.cover_image_url || '';
    const title      = song.title || 'Untitled';
    const tags       = song.metadata?.tags || song.style || '';
    const duration   = song.metadata?.duration
      ? formatDuration(song.metadata.duration) : '';
    const meta       = [tags, duration].filter(Boolean).join(' · ');

    const card = document.createElement('div');
    card.className   = `song-card ${isSelected ? 'selected' : ''}`;
    card.dataset.id  = song.id;
    card.innerHTML   = `
      <label class="checkbox-wrap song-check" title="Select">
        <input type="checkbox" ${isSelected ? 'checked' : ''} />
        <span class="checkmark"></span>
      </label>
      ${thumb
        ? `<img class="song-thumb" src="${thumb}" alt="" loading="lazy" />`
        : `<div class="song-thumb"></div>`
      }
      <div class="song-info">
        <div class="song-title" title="${escHtml(title)}">${escHtml(title)}</div>
        <div class="song-meta">${escHtml(meta)}</div>
      </div>
      <div class="song-actions">
        <button class="btn-icon" title="Download MP3" data-action="mp3">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="8 17 12 21 16 17"/><line x1="12" y1="12" x2="12" y2="21"/>
            <path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"/>
          </svg>
        </button>
        ${song.video_url ? `
        <button class="btn-icon" title="Download MP4" data-action="mp4">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
          </svg>
        </button>` : ''}
      </div>`;

    // Checkbox toggle
    const cb = card.querySelector('input[type=checkbox]');
    cb.addEventListener('change', e => {
      e.stopPropagation();
      toggleSelect(song.id, cb.checked, card);
    });

    // Download buttons
    card.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        queueSong(song, btn.dataset.action);
      });
    });

    list.appendChild(card);
  });
}

function formatDuration(secs) {
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Selection ────────────────────────────────────────────────
function toggleSelect(id, checked, card) {
  if (checked) state.selected.add(id);
  else         state.selected.delete(id);
  card.classList.toggle('selected', checked);
  updateBulkBar();
  updateSelectAll();
}

function updateBulkBar() {
  const count = state.selected.size;
  const hasAny = count > 0;
  $('btn-dl-selected').disabled = !hasAny || state.formats.size === 0;

  const sc = $('selected-count');
  sc.classList.toggle('hidden', !hasAny);
  sc.textContent = `${count} selected`;
}

function updateFormatChecks() {
  document.querySelectorAll('#format-menu input[type=checkbox]').forEach(cb => {
    cb.checked = state.formats.has(cb.value);
  });
  updateBulkBar();
}

function updateSelectAll() {
  const all = $('select-all');
  all.indeterminate = state.selected.size > 0 && state.selected.size < state.songs.length;
  all.checked       = state.selected.size === state.songs.length && state.songs.length > 0;
}

function updatePagination() {
  $('page-info').textContent = `Page ${state.page + 1}`;
  $('btn-prev').disabled = state.page === 0;
  // Disable next if we got fewer songs than page size (last page)
  $('btn-next').disabled = state.songs.length < state.pageSize;
}

// ── Queue a download ─────────────────────────────────────────
async function queueSong(song, format) {
  try {
    await sendBg('queueDownload', { song, format });
    toast(`Queued: ${song.title || 'Untitled'}`, 'success');
    updateQueueBadge();
  } catch (err) {
    toast(err.message, 'error');
  }
}

async function queueBulk(format) {
  const songs = state.songs.filter(s => state.selected.has(s.id));
  if (!songs.length) return;
  const formats = format ? [format] : [...state.formats];
  if (!formats.length) {
    toast('Select at least one format', 'error');
    return;
  }

  let count = 0;
  for (const song of songs) {
    for (const fmt of formats) {
      try {
        await sendBg('queueDownload', { song, format: fmt });
        count++;
      } catch { /* ignore per item */ }
    }
  }
  toast(`Queued ${count} items`, 'success');
  updateQueueBadge();
}

// ── Queue rendering ──────────────────────────────────────────
const STATUS_ICONS = {
  queued: `<svg class="icon-queued" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  downloading: `<svg class="icon-dl" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="8 17 12 21 16 17"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"/></svg>`,
  done: `<svg class="icon-done" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
  error: `<svg class="icon-error" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`
};

function renderQueue(items) {
  const list = $('queue-list');
  if (!items.length) {
    list.innerHTML = `
      <div class="empty-state">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="8 17 12 21 16 17"/><line x1="12" y1="12" x2="12" y2="21"/>
          <path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"/>
        </svg>
        <p>No downloads yet</p>
        <span>Head to the Library tab to start downloading.</span>
      </div>`;
    return;
  }

  list.innerHTML = '';
  [...items].reverse().forEach(item => {
    const el = document.createElement('div');
    el.className = 'queue-item';
    el.dataset.qid = item.id;

    const showBar = item.status === 'downloading' || item.status === 'done';
    const statusText =
      item.status === 'done'        ? '✓ Complete' :
      item.status === 'error'       ? `✗ ${item.error || 'Error'}` :
      item.status === 'downloading' ? `${item.progress}%` :
      'Queued';
    const textClass =
      item.status === 'done'  ? 'done'  :
      item.status === 'error' ? 'error' : '';

    el.innerHTML = `
      <div class="queue-item-top">
        <span class="queue-status-icon">${STATUS_ICONS[item.status] || ''}</span>
        <span class="queue-title" title="${escHtml(item.title)}">${escHtml(item.title || 'Untitled')}</span>
        <span class="queue-format">${item.format}</span>
        ${item.status === 'error' ? `<button class="queue-btn-retry" data-qid="${item.id}">Retry</button>` : ''}
      </div>
      ${showBar ? `
      <div class="progress-bar-wrap">
        <div class="progress-bar-fill" style="width:${item.progress}%"></div>
      </div>` : ''}
      <div class="queue-status-text ${textClass}">${statusText}</div>`;

    list.appendChild(el);
  });

  // Wire retry buttons
  list.querySelectorAll('.queue-btn-retry').forEach(btn => {
    btn.addEventListener('click', () => retryItem(btn.dataset.qid));
  });
}

async function retryItem(id) {
  try {
    const items = await sendBg('retryItem', { id });
    renderQueue(items);
  } catch (err) {
    toast(err.message, 'error');
  }
}

async function refreshQueue() {
  try {
    const items = await sendBg('getQueue');
    renderQueue(items);
    updateQueueBadge(items);
  } catch { /* ignore */ }
}

function updateQueueBadge(items) {
  const badge = $('queue-count');
  if (!items) {
    sendBg('getQueue').then(i => updateQueueBadge(i)).catch(() => {});
    return;
  }
  const active = items.filter(i => i.status === 'queued' || i.status === 'downloading').length;
  badge.textContent = active;
  badge.classList.toggle('hidden', active === 0);
}

// ── Settings ─────────────────────────────────────────────────
function loadSettings() {
  chrome.storage.local.get(['format','pageSize','folders','formats'], (data) => {
    if (data.format) {
      state.format = data.format;
      const rb = document.querySelector(`input[name="default-format"][value="${data.format}"]`);
      if (rb) rb.checked = true;
    }
    if (data.formats) {
      state.formats = new Set(data.formats);
      updateFormatChecks();
    }
    if (data.pageSize) {
      state.pageSize = parseInt(data.pageSize, 10);
      $('setting-page-size').value = data.pageSize;
    }
    if (typeof data.folders === 'boolean') {
      $('setting-folders').checked = data.folders;
    }
  });
}

function saveSettings() {
  const fmt = document.querySelector('input[name="default-format"]:checked')?.value || 'mp3';
  const ps  = $('setting-page-size').value;
  const fol = $('setting-folders').checked;
  state.format   = fmt;
  state.pageSize = parseInt(ps, 10);
  chrome.storage.local.set({ format: fmt, pageSize: ps, folders: fol, formats: [...state.formats] });
}

// ── Wire all events ──────────────────────────────────────────
function wireEvents() {

  // Tab switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn, .tab-content').forEach(el => el.classList.remove('active'));
      btn.classList.add('active');
      $(`tab-content-${btn.dataset.tab}`).classList.add('active');
      if (btn.dataset.tab === 'queue') refreshQueue();
    });
  });

  // Manual auth UI logic
  updateManualAuthUI();
  $('btn-toggle-manual').addEventListener('click', () => {
    $('manual-login-box').classList.toggle('hidden');
  });
  
  $('btn-manual-connect').addEventListener('click', () => {
    const val = $('input-manual-cookie').value.trim();
    if (!val) return toast('Please enter a valid cookie', 'error');
    chrome.storage.local.set({ manualCookie: val }, () => {
      toast('Manual token saved! Connecting...', 'success');
      showScreen('loading');
      updateManualAuthUI();
      doAuthCheck();
    });
  });

  $('btn-clear-manual').addEventListener('click', () => {
    chrome.storage.local.remove('manualCookie', () => {
      toast('Manual token cleared', 'info');
      $('input-manual-cookie').value = '';
      updateManualAuthUI();
    });
  });

  // Retry auth
  $('btn-retry-auth').addEventListener('click', () => {
    showScreen('loading');
    doAuthCheck();
  });

  // Search (debounced)
  let searchTimer;
  $('lib-search').addEventListener('input', e => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.searchQ = e.target.value.trim();
      state.page    = 0;
      loadSongs();
    }, 350);
  });

  // Playlist filter
  $('lib-playlist').addEventListener('change', e => {
    state.playlistId = e.target.value;
    state.page       = 0;
    loadSongs();
  });

  // Select all
  $('select-all').addEventListener('change', e => {
    state.songs.forEach(s => {
      if (e.target.checked) state.selected.add(s.id);
      else                  state.selected.delete(s.id);
    });
    document.querySelectorAll('.song-card input[type=checkbox]').forEach(cb => {
      cb.checked = e.target.checked;
      cb.closest('.song-card').classList.toggle('selected', e.target.checked);
    });
    updateBulkBar();
  });

  // Format picker + bulk downloads
  $('btn-format-toggle').addEventListener('click', () => {
    $('format-menu').classList.toggle('hidden');
  });
  document.addEventListener('click', e => {
    const menu = $('format-menu');
    const toggle = $('btn-format-toggle');
    if (!menu || !toggle) return;
    if (!menu.contains(e.target) && !toggle.contains(e.target)) menu.classList.add('hidden');
  });
  $('format-menu').querySelectorAll('input[type=checkbox]').forEach(cb => {
    cb.addEventListener('change', () => {
      if (cb.checked) state.formats.add(cb.value);
      else state.formats.delete(cb.value);
      chrome.storage.local.set({ formats: [...state.formats] });
      updateBulkBar();
    });
  });
  $('btn-dl-selected').addEventListener('click', () => queueBulk());

  // Pagination
  $('btn-prev').addEventListener('click', () => { state.page--; loadSongs(); });
  $('btn-next').addEventListener('click', () => { state.page++; loadSongs(); });

  // Clear done queue items
  $('btn-clear-done').addEventListener('click', async () => {
    await sendBg('clearCompleted').catch(() => {});
    refreshQueue();
  });

  // Settings auto-save
  document.querySelectorAll('input[name="default-format"]').forEach(r =>
    r.addEventListener('change', saveSettings)
  );
  $('setting-page-size').addEventListener('change', () => {
    saveSettings();
    state.page = 0;
    loadSongs();
  });
  $('setting-folders').addEventListener('change', saveSettings);

  // Listen for real-time queue updates from background
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.action === 'queueUpdate') {
      renderQueue(msg.data);
      updateQueueBadge(msg.data);
    }
  });
}
