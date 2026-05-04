var CACHE_NAME = "jarvis-pwa-v2";
var ASSETS = [
  "./index.html",
  "./app.js",
  "./manifest.json"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.map(function (key) {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
          return Promise.resolve(false);
        })
      );
    })
  );
});

self.addEventListener("fetch", function (event) {
  var requestUrl = new URL(event.request.url);
  var shouldHandle = ASSETS.some(function (asset) {
    return requestUrl.pathname.endsWith(asset.replace("./", "/"));
  });

  if (!shouldHandle) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then(function (cachedResponse) {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request).then(function (networkResponse) {
        return caches.open(CACHE_NAME).then(function (cache) {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        });
      });
    })
  );
});
