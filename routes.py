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
    get_diarrhea_records
)


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


# ============================================================
# MAVIGPT AI
# ============================================================

def ask_mavigpt(message, image_path=None):

    try:

        if image_path:

            image = Image.open(image_path)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image,
                    message or "Bu fotoğrafı incele."
                ]
            )

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message
            )

        return response.text

    except Exception as e:

        print("Gemini Hatası:", e)

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

    if file.filename == "":
        return None, None

    filename = secure_filename(file.filename)

    if not filename:
        return None, None

    upload_folder = app.config["UPLOAD_FOLDER"]

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
    # MAVIGPT
    # ========================================================

    @app.route("/", methods=["GET", "POST"])
    def home():

        mesaj = None
        cevap = None
        filename = None
        foto_path = None

        sohbetler = get_chats("normal")

        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

            foto_path, filename = upload_photo(app)

            if mesaj or foto_path:

                if mesaj:
                    prompt = mesaj
                else:
                    prompt = "Bu fotoğrafı incele."

                cevap = ask_mavigpt(
                    prompt,
                    foto_path
                )

                save_chat(
                    "normal",
                    mesaj if mesaj else "Fotoğraf",
                    cevap
                )

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

    @app.route("/doctor", methods=["GET", "POST"])
    def doctor():

        mesaj = None
        cevap = None
        filename = None
        foto_path = None
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

            # Sağlık kaydı
            if symptom or medicine or note:

                save_health_record(
                    symptom,
                    medicine,
                    note
                )

                kayit_mesaji = "✅ Kayıt edildi."

            # Fotoğraf
            foto_path, filename = upload_photo(app)

            # AI
            if mesaj or foto_path:

                if mesaj:
                    prompt = mesaj
                else:
                    prompt = "Bu sağlık fotoğrafını incele."

                cevap = ask_mavigpt(
                    prompt,
                    foto_path
                )

        kayitlar = get_health_records()

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

    @app.route("/period", methods=["GET", "POST"])
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

            save_period_record(
                start,
                end,
                note
            )

        kayitlar = get_period_records()

        return render_template(
            "period.html",
            kayitlar=kayitlar
        )


    # ========================================================
    # SİNDİRİM TAKİBİ
    # ========================================================

    @app.route("/diarrhea", methods=["GET", "POST"])
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

            save_diarrhea_record(
                date,
                count,
                condition,
                note
            )

        kayitlar = get_diarrhea_records()

        return render_template(
            "diarrhea.html",
            kayitlar=kayitlar
        )


    # ========================================================
    # İLAÇLAR
    # ========================================================

    @app.route("/medicine", methods=["GET", "POST"])
    def medicine():

        return render_template(
            "medicine.html"
        )


    # ========================================================
    # AYARLAR
    # ========================================================

    @app.route("/settings", methods=["GET", "POST"])
    def settings():

        return render_template(
            "settings.html"
            )
