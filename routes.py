import os
from flask import render_template, request
from werkzeug.utils import secure_filename
from PIL import Image
from google import genai

from database import (
    save_chat,
    get_chats,
    save_health_record,
    get_health_records,
    save_period_record,
    get_period_records,
    save_diarrhea_record,
    get_diarrhea_records,
)


# ============================================================
# GEMINI
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

client = None

if api_key:
    client = genai.Client(api_key=api_key)


# ============================================================
# MAVIGPT AI
# ============================================================

def ask_mavigpt(message, image_path=None):

    if not message:
        message = "Merhaba!"

    if client is None:
        return (
            "MaviGPT şu anda yapay zekâ bağlantısına ulaşamıyor. "
            "Railway Variables bölümünde GEMINI_API_KEY "
            "tanımlı olduğundan emin ol."
        )

    try:

        if image_path:

            image = Image.open(image_path)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image,
                    message
                ]
            )

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message
            )

        if response and response.text:
            return response.text

        return (
            "Şu anda cevap oluşturamadım. "
            "Lütfen tekrar dene."
        )

    except Exception as e:

        print("GEMINI HATASI:", repr(e))

        return (
            "MaviGPT cevap oluştururken bir sorun yaşadı. "
            "Lütfen biraz sonra tekrar dene."
        )


# ============================================================
# FOTOĞRAF YÜKLEME
# ============================================================

def upload_photo(app):

    if "photo" not in request.files:
        return None, None

    file = request.files["photo"]

    if not file:
        return None, None

    if file.filename == "":
        return None, None

    filename = secure_filename(file.filename)

    if not filename:
        return None, None

    upload_folder = app.config.get(
        "UPLOAD_FOLDER",
        os.path.join(
            app.root_path,
            "static",
            "uploads"
        )
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    path = os.path.join(
        upload_folder,
        filename
    )

    file.save(path)

    return path, filename


# ============================================================
# ROUTES
# ============================================================

def register_routes(app):

    # ========================================================
    # ANA MAVIGPT
    # ========================================================

    @app.route("/", methods=["GET", "POST"])
    def home():

        print("==============================")
        print("MAVIGPT HOME CALISTI")
        print("METHOD:", request.method)
        print("==============================")

        mesaj = ""
        cevap = ""
        filename = None

        # ----------------------------------------------------
        # SOHBET GEÇMİŞİ
        # ----------------------------------------------------

        try:

            sohbetler = get_chats("normal")

        except Exception as e:

            print(
                "SOHBETLER OKUNAMADI:",
                repr(e)
            )

            sohbetler = []

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

            print(
                "GELEN MESAJ:",
                mesaj
            )

            # ------------------------------------------------
            # FOTOĞRAF
            # ------------------------------------------------

            foto, filename = upload_photo(app)

            print(
                "FOTOĞRAF:",
                filename
            )

            # ------------------------------------------------
            # AI
            # ------------------------------------------------

            if mesaj or foto:

                if mesaj:

                    ai_mesaj = mesaj

                else:

                    ai_mesaj = (
                        "Bu fotoğrafı incele. "
                        "Gördüğün şey hakkında genel "
                        "ve anlaşılır bilgi ver."
                    )

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto
                )

                print(
                    "MAVIGPT CEVAP:",
                    cevap
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

                    print(
                        "SOHBET KAYDEDILDI"
                    )

                except Exception as e:

                    print(
                        "SOHBET KAYIT HATASI:",
                        repr(e)
                    )

        # ----------------------------------------------------
        # SAYFAYI GÖNDER
        # ----------------------------------------------------

        return render_template(
            "mavigpt.html",

            mesaj=mesaj,

            cevap=cevap,

            foto_url=(
                "/static/uploads/" + filename
                if filename
                else None
            ),

            sohbetler=sohbetler
        )


    # ========================================================
    # CEBİMDEKİ DOKTOR
    # ========================================================

    @app.route(
        "/doctor",
        methods=["GET", "POST"]
    )
    def doctor():

        mesaj = ""
        cevap = ""
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

                    kayit_mesaji = "✅ Kayıt edildi."

                except Exception as e:

                    print(
                        "SAĞLIK KAYIT HATASI:",
                        repr(e)
                    )

            # ------------------------------------------------
            # FOTOĞRAF
            # ------------------------------------------------

            foto, filename = upload_photo(app)

            # ------------------------------------------------
            # AI
            # ------------------------------------------------

            if mesaj or foto:

                ai_mesaj = (
                    mesaj
                    if mesaj
                    else
                    "Bu sağlık fotoğrafını genel "
                    "olarak incele ve anlaşılır bilgi ver."
                )

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto
                )

        # ----------------------------------------------------
        # KAYITLAR
        # ----------------------------------------------------

        try:

            kayitlar = get_health_records()

        except Exception as e:

            print(
                "SAĞLIK KAYITLARI OKUNAMADI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "doctor.html",

            mesaj=mesaj,

            cevap=cevap,

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji,

            foto_url=(
                "/static/uploads/" + filename
                if filename
                else None
            )
        )


    # ========================================================
    # REGL TAKİBİ
    # ========================================================

    @app.route(
        "/period",
        methods=["GET", "POST"]
    )
    def period():

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

                except Exception as e:

                    print(
                        "REGL KAYIT HATASI:",
                        repr(e)
                    )

        try:

            kayitlar = get_period_records()

        except Exception as e:

            print(
                "REGL KAYITLARI OKUNAMADI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "period.html",
            kayitlar=kayitlar
        )


    # ========================================================
    # SİNDİRİM TAKİBİ
    # ========================================================

    @app.route(
        "/diarrhea",
        methods=["GET", "POST"]
    )
    def diarrhea():

        if request.method == "POST":

            date = request.form.get(
                "date",
                ""
            ).strip()

            count = request.form.get(
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

            if date or count or condition or note:

                try:

                    save_diarrhea_record(
                        date,
                        count,
                        condition,
                        note
                    )

                except Exception as e:

                    print(
                        "SİNDİRİM KAYIT HATASI:",
                        repr(e)
                    )

        try:

            kayitlar = get_diarrhea_records()

        except Exception as e:

            print(
                "SİNDİRİM KAYITLARI OKUNAMADI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "diarrhea.html",
            kayitlar=kayitlar
        )
