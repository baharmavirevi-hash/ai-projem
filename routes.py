from flask import render_template, request, redirect, url_for, Response
import os
import uuid

from werkzeug.utils import secure_filename
from PIL import Image
from google import genai

from database import (
    # ========================================================
    # MAVİGPT
    # ========================================================
    save_chat,
    get_chats,
    get_chat,
    get_chat_messages,
    update_chat_title,
    delete_chat,

    # ========================================================
    # SAĞLIK
    # ========================================================
    save_health_record,
    get_health_records,

    # ========================================================
    # REGL
    # ========================================================
    save_period_record,
    get_period_records,

    # ========================================================
    # SİNDİRİM
    # ========================================================
    save_diarrhea_record,
    get_diarrhea_records,

    # ========================================================
    # İLAÇ
    # ========================================================
    save_medicine,
    get_medicines,
    delete_medicine,

    # ========================================================
    # AYARLAR
    # ========================================================
    get_settings,
    save_settings,

    # ========================================================
    # ARKADAŞ SİSTEMİ
    # ========================================================
    create_friend_room,
    get_friend_room,
    save_friend_message,
    get_friend_messages,
)


# ============================================================
# MAVİGPT CEVAP FONKSİYONU
# ============================================================

def ask_mavigpt(message, image_path=None, history=None):

    try:

        if not message:
            message = "Merhaba!"

        # ----------------------------------------------------
        # GEMINI API ANAHTARI
        # ----------------------------------------------------

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            return "GEMINI_API_KEY ayarı bulunamadı."

        # ----------------------------------------------------
        # AYARLARI AL
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

Kullanıcı kısa bir mesaj yazarsa önceki konuşmanın
bağlamını dikkate al.

Konuşmanın konusu değişirse yeni konuya uyum sağla.

Kullanıcı öğrenci ise anlatımı anlaşılır ve destekleyici yap.

Samimi ol ama aşırı resmi konuşma.

Kullanıcı Türkçe konuşuyorsa Türkçe cevap ver.
"""

        # ----------------------------------------------------
        # GEMINI CLIENT
        # ----------------------------------------------------

        client = genai.Client(
            api_key=api_key
        )

        # ----------------------------------------------------
        # KONUŞMA HAFIZASI
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # GEMINI MESAJI
        # ----------------------------------------------------

        full_message = (
            system_instruction
            + history_text
            + "\n\nYENİ KULLANICI MESAJI:\n"
            + message
        )

        # ----------------------------------------------------
        # FOTOĞRAFLI MESAJ
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # NORMAL MESAJ
        # ----------------------------------------------------

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_message
            )

        # ----------------------------------------------------
        # CEVAP
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # SOHBETLER
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # MESAJ GEÇMİŞİ
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

            foto, filename = upload_photo(
                app
            )

            # ------------------------------------------------
            # MESAJ VEYA FOTOĞRAF VARSA
            # ------------------------------------------------

            if mesaj or foto:

                if mesaj:

                    ai_mesaj = mesaj

                else:

                    ai_mesaj = (
                        "Bu fotoğrafı incele ve "
                        "genel, güvenli bilgi ver."
                    )

                # --------------------------------------------
                # HAFIZA
                # --------------------------------------------

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

                # --------------------------------------------
                # MAVİGPT
                # --------------------------------------------

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto,
                    history
                )

                # --------------------------------------------
                # SOHBETİ KAYDET
                # --------------------------------------------

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

                # --------------------------------------------
                # LİSTELERİ YENİLE
                # --------------------------------------------

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

        # ----------------------------------------------------
        # SAYFAYI GÖSTER
        # ----------------------------------------------------

        return render_template(
            "mavigpt.html",

            mesaj=mesaj,

            cevap=cevap,

            foto_url=get_photo_url(
                filename
            ),

            mesajlar=mesajlar,

            sohbetler=sohbetler
        )# ============================================================
# TEK SOHBET
# ============================================================

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


# ============================================================
# SOHBET BAŞLIĞI / MESAJI DÜZENLE
# ============================================================

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


# ============================================================
# SOHBET SİL
# ============================================================

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
        # ============================================================
# DOKTOR / CEBİMDEKİ DOKTOR
# ============================================================

    @app.route(
        "/doctor",
        methods=["GET", "POST"]
    )
    def doctor():

        mesaj = None
        cevap = None
        filename = None
        kayit_mesaji = None

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

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

            # ------------------------------------------------
            # SAĞLIK KAYDI
            # ------------------------------------------------

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

            # ------------------------------------------------
            # FOTOĞRAF
            # ------------------------------------------------

            foto, filename = upload_photo(
                app
            )

            # ------------------------------------------------
            # MAVİGPT
            # ------------------------------------------------

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

        # ----------------------------------------------------
        # SAĞLIK KAYITLARINI GETİR
        # ----------------------------------------------------

        try:

            kayitlar = get_health_records()

        except Exception as e:

            print(
                "SAĞLIK OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        # ----------------------------------------------------
        # SAYFAYI GÖSTER
        # ----------------------------------------------------

        return render_template(
            "doctor.html",

            mesaj=mesaj,

            cevap=cevap,

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji,

            foto_url=get_photo_url(
                filename
            )
        )# ============================================================
# REGL TAKİBİ
# ============================================================

    @app.route(
        "/period",
        methods=["GET", "POST"]
    )
    def period():

        kayit_mesaji = None

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

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

            # ------------------------------------------------
            # KAYIT
            # ------------------------------------------------

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

        # ----------------------------------------------------
        # KAYITLARI GETİR
        # ----------------------------------------------------

        try:

            kayitlar = get_period_records()

        except Exception as e:

            print(
                "REGL OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        # ----------------------------------------------------
        # SAYFAYI GÖSTER
        # ----------------------------------------------------

        return render_template(
            "period.html",

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji
        )
        
        
