/* Sinag Codal Studio — offline support.
   App shell: network-first (so updates arrive), cached for offline.
   Code data: cache-first by versioned URL (each file name carries a content hash in ?v=). */
const SHELL = 'sinag-codal-shell-v1';
const DATA = 'sinag-codal-data-v1';
const CORE = ['./', './index.html', './assets/app.css', './assets/app.js', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(CORE.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => (k.startsWith('sinag-app-') || k.startsWith('sinag-codal-')) && k !== SHELL && k !== DATA).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET') return;
  if (u.origin === self.location.origin && u.pathname.includes('/api/')) return;
  if (u.origin === self.location.origin && u.pathname.includes('/legacy/')) return;
  const isData = u.origin === self.location.origin && u.pathname.includes('/data/') && u.searchParams.has('v');
  if (isData) {
    e.respondWith(caches.open(DATA).then(async c => {
      const hit = await c.match(r);
      if (hit) return hit;
      const res = await fetch(r);
      if (res.ok) {
        // keep one version per file
        const base = u.origin + u.pathname;
        for (const k of await c.keys()) if (k.url.startsWith(base + '?') && k.url !== r.url) c.delete(k);
        c.put(r, res.clone());
      }
      return res;
    }));
    return;
  }
  if (u.origin === self.location.origin || /fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)) {
    e.respondWith((async () => {
      const c = await caches.open(SHELL);
      try {
        const res = await fetch(r);
        if (res.ok || res.type === 'opaque') c.put(r.mode === 'navigate' ? './' : r, res.clone());
        return res;
      } catch (err) {
        return (await c.match(r, { ignoreSearch: r.mode === 'navigate' || u.pathname.endsWith('catalog.json') })) || (r.mode === 'navigate' ? c.match('./') : Response.error());
      }
    })());
  }
});
