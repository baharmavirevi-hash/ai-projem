const CACHE_NAME = "mavigpt-v2";

const FILES_TO_CACHE = [
    "/",
    "/static/manifest.json"
];


/* =========================================
   KURULUM
========================================= */

self.addEventListener("install", event => {

    event.waitUntil(

        caches.open(CACHE_NAME)
            .then(cache => {

                return cache.addAll(
                    FILES_TO_CACHE
                );

            })

    );

    self.skipWaiting();

});


/* =========================================
   AKTİFLEŞME
========================================= */

self.addEventListener("activate", event => {

    event.waitUntil(

        caches.keys()
            .then(keys => {

                return Promise.all(

                    keys
                        .filter(key => key !== CACHE_NAME)
                        .map(key => caches.delete(key))

                );

            })

    );

    self.clients.claim();

});


/* =========================================
   SAYFA İSTEKLERİ
========================================= */

self.addEventListener("fetch", event => {

    event.respondWith(

        fetch(event.request)
            .catch(() => {

                return caches.match(
                    event.request
                );

            })

    );

});


/* =========================================
   BİLDİRİM TIKLANINCA
========================================= */

self.addEventListener(
    "notificationclick",
    event => {

        event.notification.close();

        event.waitUntil(

            clients.matchAll({
                type: "window",
                includeUncontrolled: true
            })
            .then(clientList => {

                for (const client of clientList) {

                    if ("focus" in client) {

                        return client.focus();

                    }

                }

                if (clients.openWindow) {

                    return clients.openWindow("/");

                }

            })

        );

    }
);
