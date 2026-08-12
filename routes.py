from flask import render_template, request, redirect, url_for, Response
import os
import uuid

from werkzeug.utils import secure_filename
from PIL import Image
from google import genai

from database import (
    # --------------------------------------------------------
    # MAVİGPT
    # --------------------------------------------------------
    save_chat,
    get_chats,
    get_chat,
    get_chat_messages,
    update_chat_title,
    delete_chat,

    # --------------------------------------------------------
    # SAĞLIK
    # --------------------------------------------------------
    save_health_record,
    get_health_records,

    # --------------------------------------------------------
    # REGL
    # --------------------------------------------------------
    save_period_record,
    get_period_records,

    # --------------------------------------------------------
    # SİNDİRİM
    # --------------------------------------------------------
    save_diarrhea_record,
    get_diarrhea_records,

    # --------------------------------------------------------
    # İLAÇ
    # --------------------------------------------------------
    save_medicine,
    get_medicines,
    delete_medicine,

    # --------------------------------------------------------
    # AYARLAR
    # --------------------------------------------------------
    get_settings,
    save_settings,

    # --------------------------------------------------------
    # ARKADAŞ SOHBETİ
    # --------------------------------------------------------
    create_friend_room,
    get_friend_room,
    save_friend_message,
    get_friend_messages
)


# ============================================================
# MAVİGPT
# ============================================================

def ask_mavigpt(message, image_path=None, history=None):

    try:

        if not message:
            message = "Merhaba!"

        # ----------------------------------------------------
        # GEMINI API
        # ----------------------------------------------------

        api_key = os.environ.get(
            "GEMINI_API_KEY"
        )

        if not api_key:
            return "GEMINI_API_KEY ayarı bulunamadı."

        # ----------------------------------------------------
        # AYARLAR
        # ----------------------------------------------------

        settings = get_settings()

        mode = settings["mode"]
        personality = settings["personality"]

        # ----------------------------------------------------
        # MOD
        # ----------------------------------------------------

        mode_text = {

            "normal":
                "Normal ve dengeli şekilde cevap ver.",

            "creative":
                "Daha yaratıcı, eğlenceli ve örneklerle cevap ver.",

            "study":
                "Bir öğretmen gibi açıkla. Konuyu anlaşılır şekilde öğret.",

            "concise":
                "Kısa, doğrudan ve gereksiz uzatmadan cevap ver."

        }.get(
            mode,
            "Normal ve dengeli şekilde cevap ver."
        )

        # ----------------------------------------------------
        # KİŞİLİK
        # ----------------------------------------------------

        personality_text = {

            "friendly":
                "Samimi, nazik ve arkadaşça konuş.",

            "funny":
                "Uygun yerlerde hafif mizah kullan.",

            "serious":
                "Sakin, ciddi ve düzenli konuş.",

            "teacher":
                "Sabırlı ve öğretici bir öğretmen gibi konuş."

        }.get(
            personality,
            "Samimi, nazik ve arkadaşça konuş."
        )

        # ----------------------------------------------------
        # SİSTEM TALİMATI
        # ----------------------------------------------------

        system_instruction = f"""
Sen MaviGPT'sin.

{mode_text}

{personality_text}

Türkçe konuş.

Kullanıcıya saygılı, doğal ve anlaşılır şekilde cevap ver.

Bilmediğin bilgileri uydurma.

Sağlık konularında kesin tanı koyma.
Tehlikeli veya zararlı öneriler verme.

ÖNEMLİ KONUŞMA KURALLARI:

1. Önceki konuşmaları yeni mesajı anlamak için kullan.

2. Kullanıcı aynı soruyu tekrar sorarsa:
   "Bunu daha önce sormuştun."
   "Az önce de bunu sormuştun."
   gibi gereksiz ifadeler kullanma.
   Soruyu yeniden doğal şekilde cevapla.

3. Kullanıcı kısa bir mesaj yazarsa
   ("evet", "hayır", "tamam", "olur", "pardon" gibi)
   önceki konuşmanın bağlamını dikkate al.

4. Önceki konuşmayı kullanıcı istemedikçe
   uzun uzun tekrar anlatma.

5. Konuşmanın konusu değiştiyse yeni konuya uyum sağla.

6. Kullanıcının önceki konuşmalarındaki bilgileri
   yalnızca yeni mesajı daha iyi anlamak için kullan.

7. Aynı cevabı tekrar tekrar verme.
   Kullanıcı aynı isteği yeniden yaparsa farklı,
   yararlı ve doğal bir cevap oluştur.

8. Kullanıcı bir öğrenci ise anlatımı seviyesine uygun,
   anlaşılır ve destekleyici yap.

9. Samimi ol ama aşırı resmi konuşma.

10. Kullanıcı Türkçe konuşuyorsa Türkçe cevap ver.
"""

        # ----------------------------------------------------
        # GEMINI CLIENT
        # ----------------------------------------------------

        client = genai.Client(
            api_key=api_key
        )

        # ====================================================
        # KONUŞMA HAFIZASI
        # ====================================================

        history_text = ""

        if history:

            recent_history = history[-12:]

            history_text = (
                "\n\nÖNCEKİ KONUŞMA BAĞLAMI:\n"
            )

            for item in recent_history:

                try:

                    old_message = (
                        item["message"]
                        or ""
                    )

                    old_response = (
                        item["response"]
                        or ""
                    )

                    old_message = old_message[:3000]
                    old_response = old_response[:5000]

                    history_text += (
                        "\nKullanıcı: "
                        + old_message
                        + "\nMaviGPT: "
                        + old_response
                        + "\n"
                    )

                except Exception as e:

                    print(
                        "HAFIZA ÖĞESİ OKUMA HATASI:",
                        repr(e)
                    )

        # ====================================================
        # GEMINI MESAJI
        # ====================================================

        full_message = (
            system_instruction
            + history_text
            + "\n\nYENİ KULLANICI MESAJI:\n"
            + message
        )

        # ====================================================
        # FOTOĞRAFLI MESAJ
        # ====================================================

        if image_path:

            try:

                image = Image.open(
                    image_path
                )

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        full_message,
                        image
                    ]
                )

            except Exception as e:

                print(
                    "FOTOĞRAF OKUMA HATASI:",
                    repr(e)
                )

                return (
                    "Fotoğrafı şu anda okuyamadım. "
                    "Lütfen tekrar dene."
                )

        # ====================================================
        # NORMAL MESAJ
        # ====================================================

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_message
            )

        # ====================================================
        # CEVAP
        # ====================================================

        if response and response.text:

            return response.text.strip()

        return "Şu anda cevap oluşturamadım."

    except Exception as e:

        print(
            "GEMINI HATASI:",
            repr(e)
        )

        return (
            "MaviGPT cevap oluştururken bir sorun yaşadı."
        )


# ============================================================
# FOTOĞRAF YÜKLEME
# ============================================================

def upload_photo(app):

    if "foto" not in request.files:

        return None, None

    file = request.files["foto"]

    if not file or not file.filename:

        return None, None

    original_name = secure_filename(
        file.filename
    )

    if not original_name:

        return None, None

    extension = os.path.splitext(
        original_name
    )[1].lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif"
    }

    if extension not in allowed_extensions:

        return None, None

    filename = (
        uuid.uuid4().hex
        + extension
    )

    upload_folder = app.config.get(
        "UPLOAD_FOLDER"
    )

    if not upload_folder:

        upload_folder = os.path.join(
            app.root_path,
            "static",
            "uploads"
        )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    path = os.path.join(
        upload_folder,
        filename
    )

    try:

        file.save(path)

        if os.path.exists(path):

            return path, filename

    except Exception as e:

        print(
            "FOTOĞRAF KAYDETME HATASI:",
            repr(e)
        )

    return None, None


# ============================================================
# FOTOĞRAF URL
# ============================================================

def get_photo_url(filename):

    if not filename:

        return None

    return (
        "/static/uploads/"
        + filename
    )


# ============================================================
# ROUTES
# ============================================================

def register_routes(app):

    # ========================================================
    # SERVICE WORKER
    # ========================================================

    @app.route("/service-worker.js")
    def service_worker():

        service_worker_path = os.path.join(
            app.root_path,
            "static",
            "service-worker.js"
        )

        try:

            with open(
                service_worker_path,
                "r",
                encoding="utf-8"
            ) as file:

                javascript = file.read()

            return Response(
                javascript,
                mimetype="application/javascript",
                headers={
                    "Cache-Control": "no-cache"
                }
            )

        except FileNotFoundError:

            return (
                "service-worker.js bulunamadı.",
                404
            )


    # ========================================================
    # ANA SAYFA / MAVİGPT
    # ========================================================

    @app.route(
        "/",
        methods=["GET", "POST"]
    )
    def home():

        mesaj = ""
        cevap = ""
        filename = None

        try:

            sohbetler = get_chats(
                "normal"
            )

        except Exception as e:

            print(
                "SOHBET OKUMA HATASI:",
                repr(e)
            )

            sohbetler = []

        try:

            mesajlar = get_chat_messages(
                "normal"
            )

        except Exception as e:

            print(
                "MESAJ GEÇMİŞİ HATASI:",
                repr(e)
            )

            mesajlar = []

        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

            foto, filename = upload_photo(
                app
            )

            if mesaj or foto:

                if mesaj:

                    ai_mesaj = mesaj

                else:

                    ai_mesaj = (
                        "Bu fotoğrafı incele ve "
                        "genel, güvenli bilgi ver."
                    )

                try:

                    history = get_chat_messages(
                        "normal"
                    )

                except Exception as e:

                    print(
                        "HAFIZA OKUMA HATASI:",
                        repr(e)
                    )

                    history = []

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto,
                    history
                )

                try:

                    save_chat(
                        "normal",
                        mesaj if mesaj else "Fotoğraf",
                        cevap
                    )

                except Exception as e:

                    print(
                        "SOHBET KAYIT HATASI:",
                        repr(e)
                    )

                try:

                    mesajlar = get_chat_messages(
                        "normal"
                    )

                    sohbetler = get_chats(
                        "normal"
                    )

                except Exception as e:

                    print(
                        "SOHBET YENİLEME HATASI:",
                        repr(e)
                    )

        return render_template(
            "mavigpt.html",

            mesaj=mesaj,

            cevap=cevap,

            foto_url=get_photo_url(
                filename
            ),

            mesajlar=mesajlar,

            sohbetler=sohbetler
        )


    # ========================================================
    # TEK SOHBET
    # ========================================================

    @app.route(
        "/chat/<int:chat_id>"
    )
    def chat(chat_id):

        sohbet = get_chat(
            chat_id
        )

        if not sohbet:

            return redirect(
                url_for("home")
            )

        return render_template(
            "chat.html",
            sohbet=sohbet
        )


    # ========================================================
    # SOHBET BAŞLIĞI DÜZENLE
    # ========================================================

    @app.route(
        "/chat/edit/<int:chat_id>",
        methods=["POST"]
    )
    def chat_edit(chat_id):

        title = request.form.get(
            "title",
            ""
        ).strip()

        if title:

            try:

                update_chat_title(
                    chat_id,
                    title
                )

            except Exception as e:

                print(
                    "SOHBET DÜZENLEME HATASI:",
                    repr(e)
                )

        return redirect(
            url_for(
                "chat",
                chat_id=chat_id
            )
        )


    # ========================================================
    # SOHBET SİL
    # ========================================================

    @app.route(
        "/chat/delete/<int:chat_id>",
        methods=["POST"]
    )
    def chat_delete(chat_id):

        try:

            delete_chat(
                chat_id
            )

        except Exception as e:

            print(
                "SOHBET SİLME HATASI:",
                repr(e)
            )

        return redirect(
            url_for("home")
        )


    # ========================================================
    # DOKTOR
    # ========================================================

    @app.route(
        "/doctor",
        methods=["GET", "POST"]
    )
    def doctor():

        mesaj = None
        cevap = None
        filename = None
        kayit_mesaji = None

        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

            symptom = request.form.get(
                "symptom",
                ""
            ).strip()

            medicine = request.form.get(
                "medicine",
                ""
            ).strip()

            note = request.form.get(
                "note",
                ""
            ).strip()

            if symptom or medicine or note:

                try:

                    save_health_record(
                        symptom,
                        medicine,
                        note
                    )

                    kayit_mesaji = (
                        "✅ Sağlık kaydın kaydedildi."
                    )

                except Exception as e:

                    print(
                        "SAĞLIK KAYIT HATASI:",
                        repr(e)
                    )

                    kayit_mesaji = (
                        "❌ Sağlık kaydı kaydedilemedi."
                    )

            foto, filename = upload_photo(
                app
            )

            if mesaj or foto:

                ai_mesaj = mesaj or (
                    "Bu sağlık fotoğrafı hakkında "
                    "genel ve güvenli bilgi ver. "
                    "Kesin tanı koyma."
                )

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto
                )

        try:

            kayitlar = get_health_records()

        except Exception as e:

            print(
                "SAĞLIK OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "doctor.html",

            mesaj=mesaj,

            cevap=cevap,

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji,

            foto_url=get_photo_url(
                filename
            )
        )


    # ========================================================
    # REGL
    # ========================================================

    @app.route(
        "/period",
        methods=["GET", "POST"]
    )
    def period():

        kayit_mesaji = None

        if request.method == "POST":

            start = request.form.get(
                "start_date",
                ""
            ).strip()

            end = request.form.get(
                "end_date",
                ""
            ).strip()

            note = request.form.get(
                "note",
                ""
            ).strip()

            if start:

                try:

                    save_period_record(
                        start,
                        end,
                        note
                    )

                    kayit_mesaji = (
                        "✅ Regl kaydın kaydedildi."
                    )

                except Exception as e:

                    print(
                        "REGL KAYIT HATASI:",
                        repr(e)
                    )

                    kayit_mesaji = (
                        "❌ Regl kaydı kaydedilemedi."
                    )

        try:

            kayitlar = get_period_records()

        except Exception as e:

            print(
                "REGL OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "period.html",

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # SİNDİRİM
    # ========================================================

    @app.route(
        "/diarrhea",
        methods=["GET", "POST"]
    )
    def diarrhea():

        kayit_mesaji = None

        if request.method == "POST":

            date = request.form.get(
                "date",
                ""
            ).strip()

            count_raw = request.form.get(
                "count",
                ""
            ).strip()

            condition = request.form.get(
                "condition",
                ""
            ).strip()

            note = request.form.get(
                "note",
                ""
            ).strip()

            try:

                count = max(
                    0,
                    int(count_raw or 0)
                )

            except (
                ValueError,
                TypeError
            ):

                count = 0

            if (
                date
                or count
                or condition
                or note
            ):

                try:

                    save_diarrhea_record(
                        date,
                        count,
                        condition,
                        note
                    )

                    kayit_mesaji = (
                        "✅ Sindirim kaydın kaydedildi."
                    )

                except Exception as e:

                    print(
                        "SİNDİRİM HATASI:",
                        repr(e)
                    )

                    kayit_mesaji = (
                        "❌ Sindirim kaydı kaydedilemedi."
                    )

        try:

            kayitlar = get_diarrhea_records()

        except Exception as e:

            print(
                "SİNDİRİM OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "diarrhea.html",

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # İLAÇ
    # ========================================================

    @app.route(
        "/medicine",
        methods=["GET", "POST"]
    )
    def medicine():

        kayit_mesaji = None

        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            dose = request.form.get(
                "dose",
                ""
            ).strip()

            hour = request.form.get(
                "hour",
                ""
            ).strip()

            start_date = request.form.get(
                "start_date",
                ""
            ).strip()

            if name:

                try:

                    save_medicine(
                        name,
                        dose,
                        hour,
                        start_date
                    )

                    kayit_mesaji = (
                        "✅ İlaç kaydın kaydedildi."
                    )

                except Exception as e:

                    print(
                        "İLAÇ KAYIT HATASI:",
                        repr(e)
                    )

                    kayit_mesaji = (
                        "❌ İlaç kaydı kaydedilemedi."
                    )

        try:

            kayitlar = get_medicines()

        except Exception as e:

            print(
                "İLAÇ OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "medicine.html",

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # İLAÇ SİL
    # ========================================================

    @app.route(
        "/medicine/delete/<int:medicine_id>",
        methods=["POST"]
    )
    def medicine_delete(
        medicine_id
    ):

        try:

            delete_medicine(
                medicine_id
            )

        except Exception as e:

            print(
                "İLAÇ SİLME HATASI:",
                repr(e)
            )

        return redirect(
            url_for("medicine")
        )


    # ========================================================
    # AYARLAR
    # ========================================================

    @app.route(
        "/settings",
        methods=["GET", "POST"]
    )
    def settings():

        kayit_mesaji = None

        if request.method == "POST":

            mode = request.form.get(
                "mode",
                "normal"
            ).strip()

            personality = request.form.get(
                "personality",
                "friendly"
            ).strip()

            try:

                save_settings(
                    mode,
                    personality
                )

                kayit_mesaji = (
                    "✅ Ayarların kaydedildi."
                )

            except Exception as e:

                print(
                    "AYAR KAYIT HATASI:",
                    repr(e)
                )

                kayit_mesaji = (
                    "❌ Ayarlar kaydedilemedi."
                )

        try:

            settings_data = get_settings()

        except Exception as e:

            print(
                "AYAR OKUMA HATASI:",
                repr(e)
            )

            settings_data = {
                "mode": "normal",
                "personality": "friendly"
            }

        return render_template(
            "settings.html",

            settings=settings_data,

            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # ARKADAŞ SOHBETİ ANA SAYFA
    # ========================================================

    @app.route(
        "/friends",
        methods=["GET", "POST"]
    )
    def friends():

        error = None
        room = None
        room_code = ""

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            action = request.form.get(
                "action",
                ""
            ).strip()

            # =================================================
            # YENİ ODA OLUŞTUR
            # =================================================

            if action == "create":

                room_name = request.form.get(
                    "room_name",
                    "Arkadaş Sohbeti"
                ).strip()

                if not room_name:

                    room_name = "Arkadaş Sohbeti"

                try:

                    room_code = create_friend_room(
                        room_name
                    )

                    return redirect(
                        url_for(
                            "friend_room",
                            room_code=room_code
                        )
                    )

                except Exception as e:

                    print(
                        "ARKADAŞ ODASI OLUŞTURMA HATASI:",
                        repr(e)
                    )

                    error = (
                        "Sohbet odası oluşturulamadı."
                    )

            # =================================================
            # ODAYA KATIL
            # =================================================

            elif action == "join":

                room_code = request.form.get(
                    "room_code",
                    ""
                ).strip().upper()

                if not room_code:

                    error = (
                        "Lütfen sohbet kodunu gir."
                    )

                else:

                    try:

                        room = get_friend_room(
                            room_code
                        )

                        if not room:

                            error = (
                                "Bu sohbet koduna ait oda bulunamadı."
                            )

                        else:

                            return redirect(
                                url_for(
                                    "friend_room",
                                    room_code=room_code
                                )
                            )

                    except Exception as e:

                        print(
                            "ARKADAŞ ODASI ARAMA HATASI:",
                            repr(e)
                        )

                        error = (
                            "Sohbet odası bulunurken bir hata oluştu."
                        )

        return render_template(
            "friends.html",

            room=room,

            room_code=room_code,

            error=error
        )


    # ========================================================
    # ARKADAŞ SOHBET ODASI
    # ========================================================

    @app.route(
        "/friends/<room_code>",
        methods=["GET", "POST"]
    )
    def friend_room(
        room_code
    ):

        room_code = (
            room_code
            or ""
        ).strip().upper()

        room = get_friend_room(
            room_code
        )

        if not room:

            return redirect(
                url_for("friends")
            )

        error = None

        # ----------------------------------------------------
        # MESAJ GÖNDER
        # ----------------------------------------------------

        if request.method == "POST":

            username = request.form.get(
                "username",
                ""
            ).strip()

            message = request.form.get(
                "message",
                ""
            ).strip()

            if not username:

                username = "Misafir"

            if message:

                try:

                    success = save_friend_message(
                        room_code,
                        username,
                        message
                    )

                    if not success:

                        error = (
                            "Mesaj gönderilemedi."
                        )

                except Exception as e:

                    print(
                        "ARKADAŞ MESAJI KAYIT HATASI:",
                        repr(e)
                    )

                    error = (
                        "Mesaj gönderilirken bir hata oluştu."
                    )

        # ----------------------------------------------------
        # MESAJLAR
        # ----------------------------------------------------

        try:

            messages = get_friend_messages(
                room_code
            )

        except Exception as e:

            print(
                "ARKADAŞ MESAJLARI OKUMA HATASI:",
                repr(e)
            )

            messages = []

            error = (
                "Mesajlar yüklenemedi."
            )

        return render_template(
            "friend_room.html",

            room=room,

            room_code=room_code,

            messages=messages,

            error=error
        )
