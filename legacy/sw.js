/* Sinag offline copy. Caches only the encrypted file and the icons; everything else goes to the network. */
const C = 'sinag-app-20261117153337';
const CORE = ['./', './manifest.webmanifest', './apple-touch-icon.png', './icon-192.png', './icon-512.png', './icon-maskable-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.addAll(CORE.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('sinag-app-') && k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== self.location.origin) return;
  const page = r.mode === 'navigate' || u.pathname.endsWith('/') || u.pathname.endsWith('/index.html');
  if (page) {
    e.respondWith((async () => {
      const c = await caches.open(C);
      try { const ctl = new AbortController(), t = setTimeout(() => ctl.abort(), 5000); const res = await fetch(r.url, { cache: 'no-cache', signal: ctl.signal, credentials: 'same-origin' }); clearTimeout(t); if (res.ok && res.type === 'basic') { await c.put('./', res.clone()); return res; } return (await c.match('./')) || res; }
      catch (x) { return (await c.match('./')) || Response.error(); }
    })());
    return;
  }
  e.respondWith(caches.open(C).then(c => c.match(r, { ignoreSearch: true }).then(m => m || fetch(r))));
});
