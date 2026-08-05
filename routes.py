from flask import render_template, request
import os
from werkzeug.utils import secure_filename


def register_routes(app):

    @app.route("/", methods=["GET", "POST"])
    def home():

        mesaj = None
        cevap = None
        foto = None

        if request.method == "POST":

            mesaj = request.form.get("mesaj")


            # FOTOĞRAF YÜKLEME
            if "photo" in request.files:

                file = request.files["photo"]

                if file.filename != "":

                    filename = secure_filename(file.filename)

                    upload_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )

                    file.save(upload_path)

                    foto = filename


            # Şimdilik test cevabı
            if mesaj:
    
    cevap = ask_mavigpt(mesaj)


            if foto:

                cevap = (cevap or "") + "\n📸 Fotoğraf alındı: " + foto



        return render_template(
            "mavigpt.html",
            mesaj=mesaj,
            cevap=cevap,
            sohbetler=[]
        )
