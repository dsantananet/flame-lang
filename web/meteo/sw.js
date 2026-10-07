// Increment VERSION when shipping changes to any application asset.
const VERSION='1.1.0';
const CACHE=`ignispyro-meteo-${VERSION}`;
const FILES=['./','index.html','app.mjs','engine.mjs','decisions.mjs','pwa.mjs','style.css','basemap.geojson','manifest.webmanifest','icon.svg','icon-192.png','icon-512.png','vendor/leaflet/leaflet.js','vendor/leaflet/leaflet.css','vendor/leaflet/images/layers.png','vendor/leaflet/images/layers-2x.png','vendor/leaflet/images/marker-icon.png','vendor/leaflet/images/marker-icon-2x.png','vendor/leaflet/images/marker-shadow.png'];
const urls=new Set(FILES.map(file=>new URL(file,self.registration.scope).href));
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll([...urls]))));
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const key of await caches.keys()){if(key.startsWith('ignispyro-meteo-')&&key!==CACHE)await caches.delete(key);}await self.clients.claim();})()));
self.addEventListener('message',event=>{if(event.data?.type==='APPLY_UPDATE')self.skipWaiting();});
self.addEventListener('fetch',event=>{
  // Never cache weather API requests, credentials, or files outside application scope.
  if(event.request.method!=='GET'||!urls.has(event.request.url))return;
  event.respondWith(caches.open(CACHE).then(async cache=>(await cache.match(event.request))||fetch(event.request)));
});
