from PIL import Image
from google import genai
import os

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


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
