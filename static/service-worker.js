const CACHE_NAME = "mavigpt-v3";

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
   UYGULAMADAN BİLDİRİM MESAJI
========================================= */

self.addEventListener(
    "message",
    event => {

        if (!event.data) {
            return;
        }

        if (
            event.data.type ===
            "SHOW_MEDICINE_NOTIFICATION"
        ) {

            const name =
                event.data.name ||
                "İlacın";

            const dose =
                event.data.dose ||
                "";

            let body =
                name + " zamanı geldi!";

            if (dose) {

                body +=
                    "\nDoz: " + dose;

            }

            event.waitUntil(

                self.registration.showNotification(
                    "💊 Cebimdeki Doktor",
                    {
                        body: body,

                        icon: "/static/icon-192.png",

                        badge: "/static/icon-192.png",

                        tag:
                            "medicine-" +
                            name,

                        renotify: true,

                        data: {
                            url: "/medicine"
                        }
                    }
                )

            );

        }

    }
);


/* =========================================
   BİLDİRİME TIKLANINCA
========================================= */

self.addEventListener(
    "notificationclick",
    event => {

        event.notification.close();

        const url =
            event.notification.data &&
            event.notification.data.url
                ? event.notification.data.url
                : "/medicine";

        event.waitUntil(

            clients.matchAll({
                type: "window",
                includeUncontrolled: true
            })
            .then(clientList => {

                for (
                    const client
                    of clientList
                ) {

                    if (
                        "navigate" in client
                    ) {

                        client.navigate(url);

                    }

                    if (
                        "focus" in client
                    ) {

                        return client.focus();

                    }

                }

                if (
                    clients.openWindow
                ) {

                    return clients.openWindow(
                        url
                    );

                }

            })

        );

    }
);
