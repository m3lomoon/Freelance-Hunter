/* Melo Mood service worker: the app opens offline after the first visit.
   - the page and manifest: network first (a new version shows up as soon as there is a connection), cached copy when offline
   - images, fonts, small assets: cache first, refreshed in the background
   - audio (Range requests), Supabase, ElevenLabs, Anthropic: never touched, always straight to the network
   Bump VERSION to drop old caches. */
const VERSION = 'v1';
const CACHE = 'melomood-' + VERSION;
const SHELL = ['./', 'manifest.webmanifest', 'assets/icon-192.png', 'assets/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('melomood-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || req.headers.has('range')) return;
  const sameOrigin = url.origin === location.origin;
  const font = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (!sameOrigin && !font) return;
  if (/\.(mp3|mp4|webm|m4a)$/i.test(url.pathname)) return;

  const page = req.mode === 'navigate' || /\.(webmanifest)$/.test(url.pathname);
  e.respondWith(page ? networkFirst(req) : cacheFirst(req));
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const res = await fetch(req);
    if (res.ok) cache.put(req.mode === 'navigate' ? './' : req, res.clone());
    return res;
  } catch (_) {
    return (await cache.match(req.mode === 'navigate' ? './' : req)) || Response.error();
  }
}
async function cacheFirst(req) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(req);
  const refresh = fetch(req).then(res => { if (res.ok && res.status === 200) cache.put(req, res.clone()); return res; });
  if (hit) { refresh.catch(() => {}); return hit; }
  return refresh;
}
