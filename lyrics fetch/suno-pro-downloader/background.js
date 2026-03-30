// ============================================================
// Suno Pro Downloader — Background Service Worker
// Handles: Auth (Clerk JWT), Suno API calls, File Downloads
// ============================================================

const SUNO_API   = 'https://studio-api.suno.ai';
// Prefer the current clerk host; fall back to the old one if needed
const CLERK_APIS = ['https://clerk.suno.ai', 'https://clerk.suno.com'];
const CLERK_VER  = '4.73.3';

let cachedToken  = null;
let tokenExpiry  = 0;

// ── Active download queue ────────────────────────────────────
let downloadQueue    = [];   // { song, format, status, progress, downloadId, error, tmpUrl }
let isProcessing     = false;
const CONCURRENT_DL  = 10;   // max simultaneous downloads (boosted for speed)

// ────────────────────────────────────────────────────────────
//  AUTH — get a fresh Clerk JWT using the suno.com cookies
// ────────────────────────────────────────────────────────────
async function getClerkJWT() {
  if (cachedToken && Date.now() < tokenExpiry) return cachedToken;

  // 1. Check for manual cookie override, else pull from browser
  let clientCookieValue;
  let clientCookieName = '__client';
  const storage = await chrome.storage.local.get(['manualCookie']);
  if (storage.manualCookie) {
    clientCookieValue = storage.manualCookie;
  } else {
    const COOKIE_NAMES = ['__client', '__session'];
    const COOKIE_DOMAINS = ['.suno.ai', '.app.suno.ai', '.suno.com'];

    // Try domains in priority order; pick the first cookie that exists
    let clientCookie;
    for (const domain of COOKIE_DOMAINS) {
      const domainCookies = await chrome.cookies.getAll({ domain });
      clientCookie = domainCookies.find(c => COOKIE_NAMES.includes(c.name));
      if (clientCookie) break;
    }

    if (!clientCookie) throw new Error('NOT_LOGGED_IN');
    clientCookieValue = clientCookie.value;
    clientCookieName  = clientCookie.name;
  }

  // 2. Get the active session id from Clerk
  const clientRes = await fetchWithClerkFallback(
    `/v1/client?_clerk_js_version=${CLERK_VER}`,
    { headers: { Cookie: `${clientCookieName}=${clientCookieValue}` } }
  );
  if (!clientRes.ok) throw new Error('CLERK_CLIENT_FAILED');

  const clientData = await clientRes.json();
  const sessionId  = clientData.response?.last_active_session_id;
  if (!sessionId)   throw new Error('NO_ACTIVE_SESSION');

  // 3. Exchange session for a JWT (expires ~60 s)
  const tokenRes = await fetchWithClerkFallback(
    `/v1/client/sessions/${sessionId}/tokens?_clerk_js_version=${CLERK_VER}`,
    {
      method:  'POST',
      headers: {
        Cookie:         `${clientCookieName}=${clientCookieValue}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }
  );
  if (!tokenRes.ok) throw new Error('CLERK_TOKEN_FAILED');

  const tokenData = await tokenRes.json();
  cachedToken  = tokenData.jwt;
  tokenExpiry  = Date.now() + 50_000; // refresh 10 s early
  return cachedToken;
}

// ── Authenticated fetch helper ───────────────────────────────
async function sunoFetch(path, options = {}) {
  const doFetch = async () => {
    const jwt = await getClerkJWT();
    return fetch(`${SUNO_API}${path}`, {
      ...options,
      headers: {
        Authorization:  `Bearer ${jwt}`,
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });
  };

  let res = await doFetch();
  if (res.status === 401 || res.status === 403) {
    cachedToken = null;
    tokenExpiry = 0;
    res = await doFetch();
  }

  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API_${res.status}: ${body.slice(0, 120)}`);
  }
  return res.json();
}

// Try the preferred Clerk host first; fall back to legacy host if needed
async function fetchWithClerkFallback(path, options) {
  let lastErr;
  for (const base of CLERK_APIS) {
    try {
      return await fetch(`${base}${path}`, options);
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr || new Error('CLERK_FETCH_FAILED');
}

// ────────────────────────────────────────────────────────────
//  SUBSCRIPTION CHECK — only Pro / Premier allowed
// ────────────────────────────────────────────────────────────
async function checkSubscription() {
  // Try /api/billing/info/ first, fall back to /api/session/
  let tier, username, avatarUrl;

  try {
    const billing = await sunoFetch('/api/billing/info/');
    tier      = billing.subscription_type ?? billing.plan;
    username  = billing.username ?? billing.display_name ?? '';
    avatarUrl = billing.avatar_url ?? '';
  } catch {
    const session = await sunoFetch('/api/session/');
    tier      = session.subscription_type ?? session.user?.subscription_type;
    username  = session.user?.display_name ?? session.username ?? '';
    avatarUrl = session.user?.avatar_url ?? '';
  }

  const isPremium = ['pro', 'premier'].includes((tier || '').toLowerCase());

  return { isPremium, tier: tier || 'free', username, avatarUrl };
}

// ────────────────────────────────────────────────────────────
//  LIBRARY — fetch songs & playlists
// ────────────────────────────────────────────────────────────
async function fetchSongs({ page = 0, pageSize = 20, playlistId = null } = {}) {
  let path = `/api/feed/v2/?page=${page}&page_size=${pageSize}`;
  if (playlistId) path += `&playlist_id=${encodeURIComponent(playlistId)}`;
  return sunoFetch(path);
}

async function fetchPlaylists() {
  return sunoFetch('/api/playlist/?page_size=50');
}

// ────────────────────────────────────────────────────────────
//  DOWNLOADS
// ────────────────────────────────────────────────────────────
function sanitize(name) {
  return (name || 'Untitled').replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').slice(0, 100);
}

function queueDownload(song, format = 'mp3') {
  const already = downloadQueue.find(
    d => d.song.id === song.id && d.format === format
  );
  if (already) return already.id;

  const item = {
    id:         `${song.id}_${format}_${Date.now()}`,
    song,
    format,
    status:     'queued',   // queued | downloading | done | error
    progress:   0,
    downloadId: null,
    error:      null,
    tmpUrl:     null,
    addedAt:    Date.now()
  };
  downloadQueue.push(item);
  processQueue();
  return item.id;
}

async function processQueue() {
  if (isProcessing) return;
  isProcessing = true;

  while (true) {
    const active = downloadQueue.filter(d => d.status === 'downloading').length;
    const next   = downloadQueue.find(d => d.status === 'queued');
    if (!next || active >= CONCURRENT_DL) break;

    next.status = 'downloading';
    startDownload(next);
  }

  isProcessing = false;
}

async function startDownload(item) {
  const { song, format } = item;
  const target = resolveDownloadTarget(song, format);

  if (!target) {
    item.status = 'error';
    item.error  = `No URL available for ${format}`;
    broadcast('queueUpdate', serializeQueue());
    return;
  }

  const { url, filename, mimeType, tmpUrl } = target;
  item.tmpUrl = tmpUrl || null;

  try {
    const dlId = await new Promise((resolve, reject) => {
      const opts = { url, filename, saveAs: false };
      if (mimeType) opts.mime = mimeType;
      chrome.downloads.download(opts, id => {
        if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
        else resolve(id);
      });
    });

    item.downloadId = dlId;
    broadcast('queueUpdate', serializeQueue());

    // Track completion via onChanged
    const handler = delta => {
      if (delta.id !== dlId) return;
      if (delta.state?.current === 'complete') {
        item.status   = 'done';
        item.progress = 100;
        chrome.downloads.onChanged.removeListener(handler);
        broadcast('queueUpdate', serializeQueue());
        processQueue();
        if (item.tmpUrl) setTimeout(() => URL.revokeObjectURL(item.tmpUrl), 5_000);
      } else if (delta.state?.current === 'interrupted') {
        item.status = 'error';
        item.error  = delta.error?.current || 'Download interrupted';
        chrome.downloads.onChanged.removeListener(handler);
        broadcast('queueUpdate', serializeQueue());
        processQueue();
        if (item.tmpUrl) setTimeout(() => URL.revokeObjectURL(item.tmpUrl), 5_000);
      } else if (delta.bytesReceived || delta.totalBytes) {
        // progress update
        chrome.downloads.search({ id: dlId }, results => {
          if (results[0] && results[0].totalBytes > 0) {
            item.progress = Math.round(
              (results[0].bytesReceived / results[0].totalBytes) * 100
            );
            broadcast('queueUpdate', serializeQueue());
          }
        });
      }
    };
    chrome.downloads.onChanged.addListener(handler);

  } catch (err) {
    item.status = 'error';
    item.error  = err.message;
    broadcast('queueUpdate', serializeQueue());
    processQueue();
  }
}

function serializeQueue() {
  return downloadQueue.map(d => ({
    id:       d.id,
    songId:   d.song.id,
    title:    d.song.title,
    format:   d.format,
    status:   d.status,
    progress: d.progress,
    error:    d.error,
    addedAt:  d.addedAt
  }));
}

function clearCompleted() {
  downloadQueue = downloadQueue.filter(d => d.status !== 'done' && d.status !== 'error');
  broadcast('queueUpdate', serializeQueue());
}

// ────────────────────────────────────────────────────────────
//  Download target resolution
// ────────────────────────────────────────────────────────────
function resolveDownloadTarget(song, format) {
  const safeTitle = sanitize(song.title);
  const shortId   = (song.id || 'song').slice(0, 8);

  // Text helper
  const makeTextTarget = (text, suffix) => {
    if (!text) return null;
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    return {
      url,
      filename: `Suno Pro Downloads/${safeTitle}_${shortId}_${suffix}.txt`,
      mimeType: 'text/plain',
      tmpUrl: url
    };
  };

  switch (format) {
    case 'mp3': {
      const url = song.audio_url || song.audioMp3Url || song.mp3_url;
      if (!url) return null;
      return { url, filename: `Suno Pro Downloads/${safeTitle}_${shortId}.mp3` };
    }
    case 'mp4': {
      const url = song.video_url || song.mp4_url;
      if (!url) return null;
      return { url, filename: `Suno Pro Downloads/${safeTitle}_${shortId}.mp4` };
    }
    case 'wav': {
      const url = song.wav_url || song.audio_wav_url || song.hq_audio_url || (song.audio_url && song.audio_url.endsWith('.wav') ? song.audio_url : null);
      if (!url) return null;
      return { url, filename: `Suno Pro Downloads/${safeTitle}_${shortId}.wav` };
    }
    case 'beat': {
      const url = song.instrumental_url || song.beat_url || song.backing_track_url;
      if (!url) return null;
      return { url, filename: `Suno Pro Downloads/${safeTitle}_${shortId}_beat.mp3` };
    }
    case 'zip': {
      const url = song.workspace_zip_url || song.zip_url || song.bundle_url;
      if (!url) return null;
      return { url, filename: `Suno Pro Downloads/${safeTitle}_${shortId}.zip` };
    }
    case 'prompt': {
      const text =
        song.prompt ||
        song.metadata?.prompt ||
        song.metadata?.description ||
        song.description ||
        '';
      return makeTextTarget(text, 'prompt');
    }
    case 'lyrics': {
      const text =
        song.lyrics ||
        song.metadata?.lyrics ||
        song.metadata?.full_lyrics ||
        song.metadata?.caption ||
        '';
      return makeTextTarget(text, 'lyrics');
    }
    default:
      return null;
  }
}

// ────────────────────────────────────────────────────────────
//  MESSAGING — popup ↔ background
// ────────────────────────────────────────────────────────────
function broadcast(action, data) {
  chrome.runtime.sendMessage({ action, data }).catch(() => {});
}

chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  const handle = async () => {
    switch (request.action) {

      case 'checkAuth':
        return await checkSubscription();

      case 'fetchSongs':
        return await fetchSongs(request.params || {});

      case 'fetchPlaylists':
        return await fetchPlaylists();

      case 'queueDownload':
        return { queueId: queueDownload(request.song, request.format) };

      case 'getQueue':
        return serializeQueue();

      case 'clearCompleted':
        clearCompleted();
        return { ok: true };

      case 'retryItem': {
        const item = downloadQueue.find(d => d.id === request.id);
        if (item && item.status === 'error') {
          item.status   = 'queued';
          item.progress = 0;
          item.error    = null;
          processQueue();
        }
        return serializeQueue();
      }

      default:
        throw new Error(`Unknown action: ${request.action}`);
    }
  };

  handle()
    .then(data  => sendResponse({ ok: true,  data }))
    .catch(err  => sendResponse({ ok: false, error: err.message }));

  return true; // keep channel open
});
