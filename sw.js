// Service worker - always fetch fresh from network
self.addEventListener('fetch', event => {
  if (event.request.url.includes('aveyo-dashboard.html')) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' })
        .catch(() => caches.match(event.request))
    );
  }
});
