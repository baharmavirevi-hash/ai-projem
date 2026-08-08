from flask import render_template, request
import os

from werkzeug.utils import secure_filename
from PIL import Image
from google import genai

from database import (
    save_chat,
    get_chats
)


# ==========================================
# GEMINI
# ==========================================

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


# ==========================================
# MAVIGPT
# ==========================================

def ask_mavigpt(message, image_path=None):

    try:

        if image_path:

            image = Image.open(image_path)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image,
                    f"""
Sen MaviGPT'sin.

Kurallar:

- Her zaman Türkçe konuş.
- Samimi ve yardımsever ol.
- Kullanıcının sorusuna açık ve anlaşılır cevap ver.
- Fotoğraf gönderildiyse fotoğrafı ve mesajı birlikte değerlendir.

Kullanıcının mesajı:

{message}
"""
                ]
            )

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Sen MaviGPT'sin.

Kurallar:

- Her zaman Türkçe konuş.
- Samimi ve yardımsever ol.
- Kod, ders, günlük sohbet ve genel sorularda yardımcı ol.
- Cevaplarını anlaşılır şekilde ver.

Kullanıcının mesajı:

{message}
"""
            )

        return response.text

    except Exception as e:

        return "MaviGPT şu anda cevap oluşturamadı: " + str(e)


# ==========================================
# ROUTES
# ==========================================

def register_routes(app):


    # ======================================
    # MAVIGPT
    # ======================================

    @app.route("/", methods=["GET", "POST"])
    def home():

        mesaj = None
        cevap = None
        foto_url = None

        sohbetler = get_chats("normal")


        if request.method == "POST":

            mesaj = request.form.get("mesaj", "").strip()

            filename = None
            foto_path = None


            # ------------------------------
            # FOTOĞRAF
            # ------------------------------

            if "photo" in request.files:

                file = request.files["photo"]

                if file and file.filename:

                    filename = secure_filename(
                        file.filename
                    )

                    foto_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )

                    file.save(foto_path)

                    foto_url = "uploads/" + filename


            # ------------------------------
            # MESAJ / FOTOĞRAF VARSA
            # ------------------------------

            if mesaj or foto_path:

                if foto_path:

                    cevap = ask_mavigpt(
                        mesaj or "Bu fotoğrafı incele.",
                        foto_path
                    )

                else:

                    cevap = ask_mavigpt(
                        mesaj
                    )


                # --------------------------
                # KAYDET
                # --------------------------

                save_chat(
                    "normal",
                    mesaj if mesaj else "Fotoğraf",
                    cevap,
                    foto_url
                )


                # --------------------------
                # GEÇMİŞİ YENİLE
                # --------------------------

                sohbetler = get_chats(
                    "normal"
                )


        return render_template(
            "mavigpt.html",
            mesaj=mesaj,
            cevap=cevap,
            foto=foto_path,
            foto_url=foto_url,
            sohbetler=sohbetler
        )


    # ======================================
    # CEBİMDEKİ DOKTOR
    # ======================================

    @app.route("/doctor")
    def doctor():

        return render_template(
            "doctor.html"
        )
