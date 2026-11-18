// Stacy's Time Tracker service worker — network-first so pushed updates arrive, cache for offline.
const CACHE = 'tt-cache-v2';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './splash.jpg', './icon-192.png', './icon-512.png', './icon-maskable-512.png', './apple-touch-icon.png', './img/stopwatch.png', './img/logo.png', './img/clipboard.png', './img/coins.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('message', e => { if (e.data === 'skip') self.skipWaiting(); });
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  if (url.pathname.endsWith('version.json')) return; // always live from GitHub
  e.respondWith(
    fetch(req).then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res; })
      .catch(() => caches.match(req).then(r => r || (req.mode === 'navigate' ? caches.match('./index.html') : undefined)))
  );
});
