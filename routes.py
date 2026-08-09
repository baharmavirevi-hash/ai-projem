from flask import render_template, request
import os

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

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("GEMINI HAZIR")
    except Exception as e:
        print("GEMINI BASLATMA HATASI:", repr(e))
else:
    print("UYARI: GEMINI_API_KEY bulunamadi")


# ============================================================
# MAVIGPT AI
# ============================================================

def ask_mavigpt(message, image_path=None):

    try:

        if not message:
            message = "Merhaba!"

        if client is None:
            return (
                "MaviGPT şu anda yapay zekâ servisine bağlanamıyor. "
                "Railway Variables bölümünde GEMINI_API_KEY "
                "ayarını kontrol et."
            )

        # ----------------------------------------------------
        # FOTOĞRAFLI MESAJ
        # ----------------------------------------------------

        if image_path:

            try:
                image = Image.open(image_path)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        image,
                        message
                    ]
                )

            except Exception as e:

                print(
                    "FOTOGRAF AI HATASI:",
                    repr(e)
                )

                return (
                    "Fotoğrafı işlerken bir sorun oluştu. "
                    "Lütfen tekrar dene."
                )

        # ----------------------------------------------------
        # NORMAL MESAJ
        # ----------------------------------------------------

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message
            )

        # ----------------------------------------------------
        # CEVAP
        # ----------------------------------------------------

        if response and response.text:

            return response.text

        return (
            "Şu anda cevap oluşturamadım. "
            "Lütfen tekrar dene."
        )

    except Exception as e:

        print(
            "GEMINI HATASI:",
            repr(e)
        )

        return (
            "Şu anda yanıt oluştururken bir sorun oluştu. "
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

    # Aynı isimli dosyaların üzerine yazılmasını önle
    import time

    name, extension = os.path.splitext(filename)

    filename = (
        f"{name}_{int(time.time())}{extension}"
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
    # MAVIGPT ANA SAYFA
    # ========================================================

    @app.route("/", methods=["GET", "POST"])
    def home():

        print("================================")
        print("MAVIGPT HOME CALISTI")
        print("METHOD:", request.method)
        print("================================")

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
                        "Gördüğün şey hakkında genel, "
                        "güvenli ve anlaşılır bilgi ver."
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
        # SAYFAYI GÖSTER
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

            if (
                symptom
                or medicine
                or note
            ):

                try:

                    save_health_record(
                        symptom,
                        medicine,
                        note
                    )

                    kayit_mesaji = (
                        "✅ Kayıt edildi."
                    )

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
                    "Bu sağlık fotoğrafı hakkında "
                    "genel ve güvenli bilgi ver."
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

        # ----------------------------------------------------
        # SAYFA
        # ----------------------------------------------------

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

                    print(
                        "REGL KAYDI KAYDEDILDI"
                    )

                except Exception as e:

                    print(
                        "REGL KAYIT HATASI:",
                        repr(e)
                    )

        # ----------------------------------------------------
        # KAYITLAR
        # ----------------------------------------------------

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
    # SİNDİRİM / İSHAL TAKİBİ
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

                    print(
                        "SINDIRIM KAYDI KAYDEDILDI"
                    )

                except Exception as e:

                    print(
                        "SINDIRIM KAYIT HATASI:",
                        repr(e)
                    )

        # ----------------------------------------------------
        # KAYITLAR
        # ----------------------------------------------------

        try:

            kayitlar = get_diarrhea_records()

        except Exception as e:

            print(
                "SINDIRIM KAYITLARI OKUNAMADI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "diarrhea.html",
            kayitlar=kayitlar
)
