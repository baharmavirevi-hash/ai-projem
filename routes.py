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

        return "Şu anda yanıt oluştururken bir sorun oluştu. Lütfen biraz sonra tekrar dene."


# ============================================================
# FOTOĞRAF YÜKLEME
# ============================================================

def upload_photo(app):

    if "photo" not in request.files:
        return None, None

    file = request.files["photo"]

    if file.filename == "":
        return None, None

    filename = secure
