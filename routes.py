<!DOCTYPE html>

<html lang="tr">

<head>

```
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<title>MaviGPT</title>

<style>

    * {
        box-sizing: border-box;
    }

    html,
    body {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        font-family: Arial, Helvetica, sans-serif;
    }

    body {
        background: #f5f9fc;
        color: #17212b;
        overflow: hidden;
    }

    /* ================================
       ANA UYGULAMA
    ================================= */

    .app {
        width: 100%;
        height: 100vh;
    }

    /* ================================
       SIDEBAR
    ================================= */

    .sidebar {
        position: fixed;
        top: 0;
        left: 0;

        width: 285px;
        height: 100vh;

        background: white;

        border-right: 1px solid #dfe8ee;

        z-index: 1000;

        transform: translateX(-100%);
        transition: transform 0.25s ease;

        display: flex;
        flex-direction: column;

        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.10);
    }

    .sidebar.open {
        transform: translateX(0);
    }

    .sidebar-header {
        height: 68px;
        min-height: 68px;

        display: flex;
        align-items: center;
        justify-content: space-between;

        padding: 0 15px;

        border-bottom: 1px solid #edf2f5;
    }

    .sidebar-title {
        font-size: 19px;
        font-weight: 700;
        color: #0782a8;
    }

    .close-sidebar {
        width: 42px;
        height: 42px;

        border: 0;
        border-radius: 12px;

        background: transparent;

        color: #687780;

        font-size: 28px;

        cursor: pointer;
    }

    .close-sidebar:active {
        transform: scale(.94);
    }

    /* ================================
       YENİ SOHBET
    ================================= */

    .new-chat {
        margin: 15px;

        padding: 13px 15px;

        border-radius: 13px;

        border: 1px solid #d8e8ee;

        background: #eefaff;

        color: #087c9f;

        font-weight: 600;
        font-size: 15px;

        cursor: pointer;

        text-align: left;
    }

    .new-chat:active {
        transform: scale(.98);
    }

    /* ================================
       MENÜ
    ================================= */

    .menu-section {
        padding: 4px 10px;
    }

    .menu-title {
        font-size: 11px;
        color: #8997a1;

        padding: 9px 10px 6px;

        text-transform: uppercase;
    }

    .menu-item {
        display: flex;
        align-items: center;

        gap: 12px;

        padding: 12px 11px;

        margin: 3px 0;

        border-radius: 12px;

        text-decoration: none;

        color: #25323b;

        font-size: 14px;
    }

    .menu-item:active {
        background: #eaf7fb;
    }

    .menu-icon {
        width: 28px;
        text-align: center;
        font-size: 19px;
    }

    /* ================================
       GEÇMİŞ
    ================================= */

    .history {
        flex: 1;
        overflow-y: auto;
        padding: 5px 10px 20px;
    }

    .history-title {
        font-size: 12px;
        color: #8997a1;
        padding: 10px;
    }

    .history-item {
        padding: 10px;

        border-radius: 10px;

        font-size: 13px;

        color: #45545e;

        overflow: hidden;

        white-space: nowrap;

        text-overflow: ellipsis;
    }

    /* ================================
       KARARTMA
    ================================= */

    .backdrop {
        position: fixed;

        inset: 0;

        background: rgba(0, 0, 0, .28);

        z-index: 900;

        display: none;
    }

    .backdrop.show {
        display: block;
    }

    /* ================================
       ANA ALAN
    ================================= */

    .main {
        width: 100%;
        height: 100vh;

        display: flex;
        flex-direction: column;
    }

    /* ================================
       HEADER
    ================================= */

    .header {
        height: 65px;
        min-height: 65px;

        background: white;

        border-bottom: 1px solid #dfe8ee;

        display: flex;
        align-items: center;

        padding: 0 12px;

        gap: 10px;

        z-index: 20;
    }

    .menu-button {
        width: 43px;
        height: 43px;

        border: 0;
        border-radius: 13px;

        background: #f0f8fb;

        color: #14728d;

        font-size: 24px;

        cursor: pointer;

        display: flex;
        align-items: center;
        justify-content: center;

        touch-action: manipulation;
    }

    .menu-button:active {
        transform: scale(.94);
    }

    .logo {
        width: 42px;
        height: 42px;

        border-radius: 14px;

        background: #d9f5ff;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 22px;
    }

    .header-info {
        min-width: 0;
    }

    .title {
        font-size: 17px;
        font-weight: 700;
    }

    .status {
        color: #29a56f;

        font-size: 11px;

        margin-top: 3px;
    }

    /* ================================
       CHAT
    ================================= */

    .chat {
        flex: 1;

        overflow-y: auto;

        padding: 25px 12px 120px;

        scroll-behavior: smooth;
    }

    .chat-inner {
        width: 100%;
        max-width: 850px;
        margin: auto;
    }

    /* ================================
       HOŞ GELDİN
    ================================= */

    .welcome {
        text-align: center;

        margin: 65px auto 40px;

        max-width: 500px;
    }

    .welcome-logo {
        width: 75px;
        height: 75px;

        margin: auto;

        border-radius: 24px;

        background: #d9f5ff;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 42px;
    }

    .welcome h1 {
        margin: 18px 0 8px;
        font-size: 25px;
    }

    .welcome p {
        margin: 0;

        color: #72808a;

        line-height: 1.6;

        font-size: 14px;
    }

    /* ================================
       MESAJ
    ================================= */

    .message {
        width: 100%;

        display: flex;

        gap: 9px;

        margin-bottom: 20px;

        align-items: flex-start;
    }

    .avatar {
        width: 36px;
        min-width: 36px;

        height: 36px;

        border-radius: 12px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 18px;
    }

    .user-avatar {
        background: #e2eaff;
    }

    .bot-avatar {
        background: #d9f5ff;
    }

    .message-content {
        max-width: calc(100% - 45px);
    }

    .message-name {
        font-size: 11px;

        color: #84919a;

        margin: 0 0 5px 3px;
    }

    .bubble {
        padding: 12px 15px;

        border-radius: 17px;

        line-height: 1.55;

        font-size: 15px;

        word-break: break-word;

        white-space: pre-wrap;
    }

    .user-bubble {
        background: #dcecff;

        border-top-left-radius: 5px;
    }

    .bot-bubble {
        background: white;

        border: 1px solid #dfe7eb;

        border-top-left-radius: 5px;
    }

    .photo-preview {
        margin-top: 8px;

        max-width: 260px;
        max-height: 300px;

        border-radius: 14px;

        display: block;

        border: 1px solid #dbe6eb;
    }

    /* ================================
       INPUT ALANI
    ================================= */

    .input-area {
        position: fixed;

        bottom: 0;
        left: 0;
        right: 0;

        padding: 8px 9px 10px;

        background:
            linear-gradient(
                to top,
                #f5f9fc 75%,
                rgba(245,249,252,.85)
            );

        z-index: 30;
    }

    .input-container {
        width: 100%;

        max-width: 850px;

        margin: auto;
    }

    .file-name {
        display: none;

        font-size: 12px;

        color: #087c9f;

        padding: 4px 10px;
    }

    .file-name.show {
        display: block;
    }

    .input-box {
        min-height: 54px;

        width: 100%;

        background: white;

        border: 1px solid #d5e2e8;

        border-radius: 19px;

        display: flex;

        align-items: center;

        padding: 5px 6px;

        box-shadow:
            0 4px 18px rgba(0,0,0,.06);
    }

    .plus {
        width: 42px;
        min-width: 42px;

        height: 42px;

        display: flex;

        align-items: center;
        justify-content: center;

        font-size: 27px;

        color: #60717c;

        cursor: pointer;

        border-radius: 12px;

        touch-action: manipulation;
    }

    .plus:active {
        background: #f1f7fa;
        transform: scale(.94);
    }

    #mesaj {
        flex: 1;

        min-width: 0;

        height: 42px;

        border: 0;

        outline: 0;

        font-size: 15px;

        padding: 8px 7px;

        background: transparent;

        color: #17212b;
    }

    #mesaj::placeholder {
        color: #9aa7ae;
    }

    .send {
        width: 43px;
        min-width: 43px;

        height: 43px;

        border: 0;

        border-radius: 14px;

        background: #0782a8;

        color: white;

        font-size: 19px;

        cursor: pointer;

        touch-action: manipulation;
    }

    .send:active {
        transform: scale(.94);
    }

    #photoInput {
        display: none;
    }

    /* ================================
       MOBİL
    ================================= */

    @media (max-width: 600px) {

        .sidebar {
            width: 285px;
        }

        .chat {
            padding:
                20px
                9px
                125px;
        }

        .welcome {
            margin-top: 50px;
        }

        .welcome-logo {
            width: 68px;
            height: 68px;
            font-size: 38px;
        }

        .welcome h1 {
            font-size: 22px;
        }

        .bubble {
            font-size: 14px;
            padding: 11px 13px;
        }

        .avatar {
            width: 34px;
            min-width: 34px;
            height: 34px;
            font-size: 16px;
        }

        .message-content {
            max-width: calc(100% - 43px);
        }

        .header {
            height: 62px;
            min-height: 62px;
        }

        .title {
            font-size: 16px;
        }

        .input-area {
            padding: 7px 7px 9px;
        }

        .input-box {
            min-height: 52px;
        }

        #mesaj {
            font-size: 14px;
        }
    }

</style>
```

</head>

<body>

<div class="app">

```
<!-- ================================
     SIDEBAR
================================= -->

<aside
    class="sidebar"
    id="sidebar">

    <div class="sidebar-header">

        <div class="sidebar-title">
            🩵 MaviGPT
        </div>

        <button
            class="close-sidebar"
            type="button"
            id="closeSidebarButton">

            ×

        </button>

    </div>


    <button
        class="new-chat"
        type="button"
        id="newChatButton">

        ＋ Yeni sohbet

    </button>


    <div class="menu-section">

        <div class="menu-title">
            MaviGPT
        </div>


        <a
            href="/"
            class="menu-item">

            <span class="menu-icon">💬</span>

            <span>Yeni sohbet</span>

        </a>


        <a
            href="/doctor"
            class="menu-item">

            <span class="menu-icon">🩺</span>

            <span>Cebimdeki Doktor</span>

        </a>


        <a
            href="/period"
            class="menu-item">

            <span class="menu-icon">📅</span>

            <span>Regl Takibi</span>

        </a>


        <a
            href="/diarrhea"
            class="menu-item">

            <span class="menu-icon">📝</span>

            <span>Sindirim Takibi</span>

        </a>

    </div>


    <div class="history">

        <div class="history-title">
            Son sohbetler
        </div>


        {% if sohbetler %}

            {% for sohbet in sohbetler %}

                <div class="history-item">

                    {% if sohbet[1] is defined %}

                        {{ sohbet[1] }}

                    {% else %}

                        Sohbet

                    {% endif %}

                </div>

            {% endfor %}

        {% else %}

            <div class="history-item">
                Henüz sohbet yok.
            </div>

        {% endif %}

    </div>

</aside>


<!-- KARARTMA -->

<div
    class="backdrop"
    id="backdrop">
</div>


<!-- ================================
     ANA
================================= -->

<main class="main">


    <header class="header">

        <button
            class="menu-button"
            type="button"
            id="menuButton"
            aria-label="Menüyü aç">

            ☰

        </button>


        <div class="logo">
            🩵
        </div>


        <div class="header-info">

            <div class="title">
                MaviGPT
            </div>

            <div class="status">
                ● Çevrimiçi
            </div>

        </div>

    </header>


    <!-- ================================
         CHAT
    ================================= -->

    <section
        class="chat"
        id="chat">

        <div class="chat-inner">


            {% if not mesaj and not cevap %}

                <div class="welcome">

                    <div class="welcome-logo">
                        🩵
                    </div>

                    <h1>
                        Merhaba Bahar! 👋
                    </h1>

                    <p>
                        Ben MaviGPT.
                        <br>
                        Sana nasıl yardımcı olabilirim?
                    </p>

                </div>

            {% endif %}


            {% if mesaj %}

                <div class="message">

                    <div class="avatar user-avatar">
                        👤
                    </div>

                    <div class="message-content">

                        <div class="message-name">
                            Sen
                        </div>

                        <div class="bubble user-bubble">
                            {{ mesaj }}
                        </div>


                        {% if foto_url %}

                            <img
                                src="{{ foto_url }}"
                                class="photo-preview"
                                alt="Gönderilen fotoğraf">

                        {% endif %}

                    </div>

                </div>

            {% endif %}


            {% if cevap %}

                <div class="message">

                    <div class="avatar bot-avatar">
                        🩵
                    </div>

                    <div class="message-content">

                        <div class="message-name">
                            MaviGPT
                        </div>

                        <div class="bubble bot-bubble">
                            {{ cevap }}
                        </div>

                    </div>

                </div>

            {% endif %}


        </div>

    </section>


    <!-- ================================
         MESAJ FORMU
    ================================= -->

    <div class="input-area">

        <div class="input-container">

            <div
                class="file-name"
                id="fileName">
            </div>


            <form
                id="chatForm"
                action="/"
                method="POST"
                enctype="multipart/form-data">

                <div class="input-box">


                    <label
                        class="plus"
                        for="photoInput"
                        title="Fotoğraf ekle">

                        ＋

                    </label>


                    <input
                        type="file"
                        id="photoInput"
                        name="photo"
                        accept="image/*">


                    <input
                        type="text"
                        id="mesaj"
                        name="mesaj"
                        autocomplete="off"
                        placeholder="Mesajını yaz..."
                        aria-label="Mesajını yaz">


                    <button
                        class="send"
                        type="submit"
                        aria-label="Gönder">

                        ➤

                    </button>

                </div>

            </form>

        </div>

    </div>


</main>
```

</div>

<!-- ================================
     JAVASCRIPT
================================= -->

<script>

    document.addEventListener("DOMContentLoaded", function () {

        const sidebar =
            document.getElementById("sidebar");

        const menuButton =
            document.getElementById("menuButton");

        const closeButton =
            document.getElementById("closeSidebarButton");

        const backdrop =
            document.getElementById("backdrop");

        const newChatButton =
            document.getElementById("newChatButton");

        const chatForm =
            document.getElementById("chatForm");

        const messageInput =
            document.getElementById("mesaj");

        const photoInput =
            document.getElementById("photoInput");

        const fileName =
            document.getElementById("fileName");


        /* ==========================
           MENÜ AÇ
        ========================== */

        function openMenu() {

            sidebar.classList.add("open");

            backdrop.classList.add("show");

        }


        /* ==========================
           MENÜ KAPAT
        ========================== */

        function closeMenu() {

            sidebar.classList.remove("open");

            backdrop.classList.remove("show");

        }


        /* ==========================
           ÜÇ ÇİZGİ
        ========================== */

        if (menuButton) {

            menuButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    openMenu();

                }
            );

        }


        /* ==========================
           X
        ========================== */

        if (closeButton) {

            closeButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    closeMenu();

                }
            );

        }


        /* ==========================
           KARARTMAYA BASINCA KAPAT
        ========================== */

        if (backdrop) {

            backdrop.addEventListener(
                "click",
                function () {

                    closeMenu();

                }
            );

        }


        /* ==========================
           YENİ SOHBET
        ========================== */

        if (newChatButton) {

            newChatButton.addEventListener(
                "click",
                function () {

                    window.location.href = "/";

                }
            );

        }


        /* ==========================
           FOTOĞRAF
        ========================== */

        if (photoInput) {

            photo
