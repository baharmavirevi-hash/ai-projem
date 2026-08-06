from flask import render_template, request
import os

from werkzeug.utils import secure_filename
from PIL import Image
from google import genai

from database import (
    save_chat,
    get_chats,
    save_health_record,
    get_health_records
)


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
                    f"""
Sen MaviGPT'sin.

Kurallar:
- Türkçe konuş.
- Samimi ve yardımsever ol.
- Fotoğrafı ve mesajı birlikte değerlendir.

Kullanıcı:
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
- Türkçe konuş.
- Samimi ve yardımsever ol.
- Kod, ders ve sohbet konularında yardımcı ol.

Kullanıcı:
{message}
"""
            )


        return response.text


    except Exception as e:

        return "Bir hata oluştu: " + str(e)





def save_uploaded_photo(app):

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





def register_routes(app):


    @app.route("/", methods=["GET","POST"])
    def home():

        mesaj = None
        cevap = None
        filename = None


        sohbetler = get_chats("normal")


        if request.method == "POST":

            mesaj = request.form.get("mesaj")


            foto, filename = save_uploaded_photo(app)


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
            foto_url=("uploads/"+filename) if filename else None,
            sohbetler=sohbetler
        )






    @app.route("/doctor", methods=["GET","POST"])
    def doctor():

        mesaj = None
        cevap = None
        kayit_mesaji = None
        filename = None


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

                kayit_mesaji = "✅ Sağlık kaydı kaydedildi."



            foto, filename = save_uploaded_photo(app)



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
            foto_url=("uploads/"+filename) if filename else None
    )
