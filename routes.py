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
# MAVIGPT
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

    os.makedirs(upload_folder, exist_ok=True)

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

    mesaj = ""
    cevap = ""
    filename = None

    try:
        sohbetler = get_chats("normal")
    except Exception as e:
        print("SOHBET HATASI:", e)
        sohbetler = []

    if request.method == "POST":

        mesaj = request.form.get("mesaj", "").strip()

        foto, filename = upload_photo(app)

        if mesaj or foto:

            cevap = ask_mavigpt(
                mesaj if mesaj else "Bu fotoğrafı incele.",
                foto
            )

            try:
                save_chat(
                    "normal",
                    mesaj if mesaj else "Fotoğraf",
                    cevap
                )
            except Exception as e:
                print("KAYIT HATASI:", e)

    return render_template(
        "mavigpt.html",
        mesaj=mesaj,
        cevap=cevap,
        foto_url=(
            "/static/uploads/" + filename
            if filename else None
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

                try:

                    save_health_record(
                        symptom,
                        medicine,
                        note
                    )

                    kayit_mesaji = "✅ Kayıt edildi."

                except Exception as e:

                    print("Sağlık kayıt hatası:", e)

            # Fotoğraf
            foto, filename = upload_photo(app)

            # AI
            if mesaj or foto:

                cevap = ask_mavigpt(
                    mesaj or "Bu sağlık fotoğrafını incele.",
                    foto
                )

        try:

            kayitlar = get_health_records()

        except Exception:

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

            if start:

                try:

                    save_period_record(
                        start,
                        end,
                        note
                    )

                except Exception as e:

                    print(
                        "Regl kayıt hatası:",
                        e
                    )

        try:

            kayitlar = get_period_records()

        except Exception:

            kayitlar = []

        return render_template(
            "period.html",
            kayitlar=kayitlar
        )


    # ========================================================
    # SİNDİRİM / İSHAL TAKİBİ
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
                        "Sindirim kayıt hatası:",
                        e
                    )

        try:

            kayitlar = get_diarrhea_records()

        except Exception:

            kayitlar = []

        return render_template(
            "diarrhea.html",
            kayitlar=kayitlar
    )
