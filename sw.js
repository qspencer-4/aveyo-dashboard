const VERSION = 'v146';

// Don't intercept backend / API calls. The cache layer is for static
// shell assets only; intercepting POSTs to api.podio.com or our backend
// just adds a "cache.put threw because POST" failure to every request.
const PASSTHROUGH_HOSTS = [
  'api.podio.com',
  'podio.com',
  'aveyo.aiwhileyousleeping.com',
  'palmetto.finance',
];

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  let url;
  try { url = new URL(req.url); } catch(e) { return; }

  // Pass backend/API requests straight through without caching.
  if (PASSTHROUGH_HOSTS.some(h => url.hostname === h || url.hostname.endsWith('.'+h))) {
    return; // Don't call respondWith — browser handles natively.
  }

  // Don't try to cache non-GET (Cache API rejects PUT/POST/DELETE).
  if (req.method !== 'GET') {
    return;
  }

  // Network-first for static shell, cache fallback when offline.
  event.respondWith(
    fetch(req).then(response => {
      const clone = response.clone();
      caches.open(VERSION).then(cache => cache.put(req, clone)).catch(()=>{});
      return response;
    }).catch(() => caches.match(req))
  );
});
