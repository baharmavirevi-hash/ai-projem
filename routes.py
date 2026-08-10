from flask import render_template, request, redirect, url_for
import os
import uuid

from werkzeug.utils import secure_filename
from PIL import Image
from google import genai

from database import (
    save_chat,
    get_chats,
    get_chat,
    save_health_record,
    get_health_records,
    save_period_record,
    get_period_records,
    save_diarrhea_record,
    get_diarrhea_records,
    save_medicine,
    get_medicines,
    delete_medicine,
    get_settings,
    save_settings
)


# ============================================================
# MAVİGPT
# ============================================================

def ask_mavigpt(message, image_path=None):

    try:

        if not message:
            message = "Merhaba!"

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            return "GEMINI_API_KEY ayarı bulunamadı."

        settings = get_settings()

        mode = settings["mode"]
        personality = settings["personality"]

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

        system_instruction = f"""
Sen MaviGPT'sin.

{mode_text}

{personality_text}

Türkçe konuş.
Kullanıcıya saygılı davran.
Bilmediğin bilgileri uydurma.
Sağlık konularında kesin tanı koyma.
Tehlikeli veya zararlı öneriler verme.
"""

        client = genai.Client(
            api_key=api_key
        )

        full_message = (
            system_instruction
            + "\n\nKullanıcının mesajı:\n"
            + message
        )

        if image_path:

            try:

                image = Image.open(image_path)

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

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_message
            )

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
# FOTOĞRAF
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
        uuid.uuid4().hex +
        extension
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


def get_photo_url(filename):

    if not filename:
        return None

    return "/static/uploads/" + filename


# ============================================================
# ROUTES
# ============================================================

def register_routes(app):

    # ========================================================
    # ANA SAYFA / MAVİGPT
    # ========================================================

    @app.route("/", methods=["GET", "POST"])
    def home():

        mesaj = ""
        cevap = ""
        filename = None

        try:
            sohbetler = get_chats("normal")
        except Exception as e:
            print("SOHBET OKUMA HATASI:", repr(e))
            sohbetler = []

        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

            foto, filename = upload_photo(app)

            if mesaj or foto:

                if mesaj:
                    ai_mesaj = mesaj
                else:
                    ai_mesaj = (
                        "Bu fotoğrafı incele ve "
                        "genel, güvenli bilgi ver."
                    )

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto
                )

                try:

                    save_chat(
                        "normal",
                        mesaj if mesaj else "Fotoğraf",
                        cevap
                    )

                    sohbetler = get_chats(
                        "normal"
                    )

                except Exception as e:

                    print(
                        "SOHBET KAYIT HATASI:",
                        repr(e)
                    )

        return render_template(
            "mavigpt.html",
            mesaj=mesaj,
            cevap=cevap,
            foto_url=get_photo_url(filename),
            sohbetler=sohbetler
        )


    # ========================================================
    # TEK SOHBET
    # ========================================================

    @app.route("/chat/<int:chat_id>")
    def chat(chat_id):

        sohbet = get_chat(chat_id)

        if not sohbet:
            return redirect(url_for("home"))

        return render_template(
            "chat.html",
            sohbet=sohbet
        )


    # ========================================================
    # DOKTOR
    # ========================================================

    @app.route("/doctor", methods=["GET", "POST"])
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

            foto, filename = upload_photo(app)

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
            print("SAĞLIK OKUMA HATASI:", repr(e))
            kayitlar = []

        return render_template(
            "doctor.html",
            mesaj=mesaj,
            cevap=cevap,
            kayitlar=kayitlar,
            kayit_mesaji=kayit_mesaji,
            foto_url=get_photo_url(filename)
        )


    # ========================================================
    # REGL
    # ========================================================

    @app.route("/period", methods=["GET", "POST"])
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
            print("REGL OKUMA HATASI:", repr(e))
            kayitlar = []

        return render_template(
            "period.html",
            kayitlar=kayitlar,
            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # SİNDİRİM
    # ========================================================

    @app.route("/diarrhea", methods=["GET", "POST"])
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
                count = max(0, int(count_raw or 0))
            except (ValueError, TypeError):
                count = 0

            if date or count or condition or note:

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
            print("SİNDİRİM OKUMA HATASI:", repr(e))
            kayitlar = []

        return render_template(
            "diarrhea.html",
            kayitlar=kayitlar,
            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # İLAÇ
    # ========================================================

    @app.route("/medicine", methods=["GET", "POST"])
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
            print("İLAÇ OKUMA HATASI:", repr(e))
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
    def medicine_delete(medicine_id):

        try:
            delete_medicine(medicine_id)
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
            print("AYAR OKUMA HATASI:", repr(e))
            settings_data = {
                "mode": "normal",
                "personality": "friendly"
            }

        return render_template(
            "settings.html",
            settings=settings_data,
            kayit_mesaji=kayit_mesaji
    )
