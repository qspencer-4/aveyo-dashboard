const VERSION = 'v70';

// On install - skip waiting to activate immediately
self.addEventListener('install', event => {
  self.skipWaiting();
});

// On activate - take control of all pages immediately  
self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
});

// On fetch - always get fresh HTML from network, cache everything else normally
self.addEventListener('fetch', event => {
  if (event.request.url.includes('aveyo-dashboard.html')) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' })
        .catch(() => caches.match(event.request))
    );
  }
});
