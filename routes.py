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


# =========================
# GEMINI
# =========================

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def ask_mavigpt(message, image_path=None):

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

        return response.text

    except Exception as e:

        return "Hata oluştu: " + str(e)


# =========================
# FOTOĞRAF YÜKLEME
# =========================

def upload_photo(app):

    if "photo" not in request.files:
        return None, None

    file = request.files["photo"]

    if file.filename == "":
        return None, None

    filename = secure_filename(file.filename)

    path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(path)

    return path, filename


# =========================
# ROUTES
# =========================

def register_routes(app):

    # =========================
    # MAVIGPT
    # =========================

    @app.route("/", methods=["GET", "POST"])
    def home():

        mesaj = None
        cevap = None
        filename = None

        sohbetler = get_chats("normal")

        if request.method == "POST":

            mesaj = request.form.get("mesaj")

            foto, filename = upload_photo(app)

            if mesaj or foto:

                cevap = ask_mavigpt(
                    mesaj or "Bu fotoğrafı incele.",
                    foto
                )

                save_chat(
                    "normal",
                    mesaj or "Fotoğraf",
                    cevap
                )

        return render_template(
            "mavigpt.html",
            mesaj=mesaj,
            cevap=cevap,
            foto_url=(
                "uploads/" + filename
                if filename
                else None
            ),
            sohbetler=sohbetler
        )


    # =========================
    # CEBİMDEKİ DOKTOR
    # =========================

    @app.route("/doctor", methods=["GET", "POST"])
    def doctor():

        mesaj = None
        cevap = None
        filename = None
        kayit_mesaji = None

        if request.method == "POST":

            mesaj = request.form.get("mesaj")

            symptom = request.form.get("symptom")
            medicine = request.form.get("medicine")
            note = request.form.get("note")

            if symptom or medicine or note:

                save_health_record(
                    symptom,
                    medicine,
                    note
                )

                kayit_mesaji = "✅ Kayıt edildi."

            foto, filename = upload_photo(app)

            if mesaj or foto:

                cevap = ask_mavigpt(
                    mesaj or "Bu sağlık fotoğrafını incele.",
                    foto
                )

        kayitlar = get_health_records()

        return render_template(
            "doctor.html",
            mesaj=mesaj,
            cevap=cevap,
            kayitlar=kayitlar,
            kayit_mesaji=kayit_mesaji,
            foto_url=(
                "uploads/" + filename
                if filename
                else None
            )
        )


    # =========================
    # REGL TAKİBİ
    # =========================

    @app.route("/period", methods=["GET", "POST"])
    def period():

        if request.method == "POST":

            start = request.form.get("start_date")
            end = request.form.get("end_date")
            note = request.form.get("note")

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


    # =========================
    # SİNDİRİM TAKİBİ
    # =========================

    @app.route("/diarrhea", methods=["GET", "POST"])
    def diarrhea():

        if request.method == "POST":

            date = request.form.get("date")
            count = request.form.get("count")
            condition = request.form.get("condition")
            note = request.form.get("note")

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


    # =========================
    # İLAÇLARIM
    # =========================

    @app.route("/medicine")
    def medicine():

        return render_template(
            "medicine.html"
        )


    # =========================
    # AYARLAR
    # =========================

    @app.route("/settings")
    def settings():

        return render_template(
            "settings.html"
        )
