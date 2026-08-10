const CACHE_NAME = "mavigpt-v2";

const FILES_TO_CACHE = [
    "/",
    "/doctor",
    "/medicine",
    "/period",
    "/diarrhea",
    "/static/manifest.json"
];

self.addEventListener("install", function (event) {

    event.waitUntil(

        caches.open(CACHE_NAME).then(function (cache) {

            return cache.addAll(FILES_TO_CACHE);

        })

    );

    self.skipWaiting();
});


self.addEventListener("activate", function (event) {

    event.waitUntil(

        caches.keys().then(function (cacheNames) {

            return Promise.all(

                cacheNames.map(function (cacheName) {

                    if (cacheName !== CACHE_NAME) {

                        return caches.delete(cacheName);

                    }

                })

            );

        })

    );

    self.clients.claim();
});


self.addEventListener("fetch", function (event) {

    event.respondWith(

        fetch(event.request)

            .then(function (response) {

                return response;

            })

            .catch(function () {

                return caches.match(event.request);

            })

    );

});
