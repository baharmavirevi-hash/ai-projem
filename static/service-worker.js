const CACHE_NAME = "mavigpt-v4";

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

    /*
       POST, WebSocket vb. istekleri
       cache sistemine sokmuyoruz.
    */

    if (event.request.method !== "GET") {
        return;
    }

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


        /* =====================================
           İLAÇ BİLDİRİMİ
        ===================================== */

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

                        icon:
                            "/static/icon-192.png",

                        badge:
                            "/static/icon-192.png",

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


        /* =====================================
           ARKADAŞ GÖRÜNTÜLÜ ARAMA BİLDİRİMİ
        ===================================== */

        if (
            event.data.type ===
            "SHOW_FRIEND_CALL_NOTIFICATION"
        ) {

            const caller =
                event.data.caller ||
                "Arkadaşın";

            const roomCode =
                event.data.room_code ||
                "";

            const url =
                event.data.url ||
                (
                    roomCode
                        ? "/friends/" +
                          encodeURIComponent(roomCode)
                        : "/friends"
                );


            event.waitUntil(

                self.registration.showNotification(
                    "📹 Görüntülü arama",
                    {

                        body:
                            caller +
                            " seni görüntülü arıyor.",

                        icon:
                            "/static/icon-192.png",

                        badge:
                            "/static/icon-192.png",

                        tag:
                            "friend-call-" +
                            roomCode,

                        renotify: true,

                        requireInteraction: true,

                        vibrate: [
                            200,
                            100,
                            200,
                            100,
                            400
                        ],

                        data: {
                            url: url,
                            type: "friend_call",
                            room_code: roomCode,
                            caller: caller
                        },

                        actions: [
                            {
                                action: "open",
                                title: "📹 Aç"
                            },

                            {
                                action: "dismiss",
                                title: "❌ Kapat"
                            }
                        ]

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


        const notificationData =
            event.notification.data || {};


        /*
           Kapat butonuna basıldıysa
           hiçbir şey açma.
        */

        if (
            event.action ===
            "dismiss"
        ) {
            return;
        }


        const url =
            notificationData.url ||
            "/";


        event.waitUntil(

            clients.matchAll({

                type: "window",

                includeUncontrolled: true

            })

            .then(clientList => {

                /*
                   Uygulama zaten açıksa
                   mevcut pencereyi kullan.
                */

                for (
                    const client
                    of clientList
                ) {

                    if (
                        "navigate" in client
                    ) {

                        client.navigate(
                            url
                        );

                    }

                    if (
                        "focus" in client
                    ) {

                        return client.focus();

                    }

                }


                /*
                   Uygulama kapalıysa
                   yeni pencere aç.
                */

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
