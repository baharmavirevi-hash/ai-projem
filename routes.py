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
            def ask_mavigpt(message, image_path=None):
    try:

        if image_path:
            if mesaj:

    if foto:
        cevap = ask_mavigpt(
            mesaj,
            os.path.join(app.config["UPLOAD_FOLDER"], foto)
        )
    else:
        cevap = ask_mavigpt(mesaj)
            image = Image.open(image_path)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image,
                    f"""
Sen MaviGPT'sin.

Her zaman Türkçe konuş.
Samimi ol.
Kullanıcının mesajını ve fotoğrafını birlikte değerlendir.

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

Her zaman Türkçe konuş.

Kullanıcının mesajı:
{message}
"""
            )

        return response.text

    except Exception as e:
        return f"Hata oluştu: {e}"
        
