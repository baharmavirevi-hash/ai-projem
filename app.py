import os

from flask import Flask


# ============================================================
# FLASK UYGULAMASI
# ============================================================

app = Flask(__name__)


# ============================================================
# GİZLİ ANAHTAR
# ============================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "mavigpt-development-secret-key"
)
from datetime import timedelta

app.permanent_session_lifetime = timedelta(days=30)

# ============================================================
# DATABASE
# ============================================================

from database import init_db

init_db()


# ============================================================
# ROUTES
# ============================================================

from routes import register_routes

register_routes(app)


# ============================================================
# MAVİGPT
# ============================================================

def ask_mavigpt(
    mesaj,
    foto=None,
    history=None
):
    """
    MaviGPT cevap sistemi.
    """

    try:

        from google import genai

        api_key = os.environ.get(
            "GEMINI_API_KEY"
        )

        if not api_key:

            return (
                "MaviGPT şu anda yapılandırılmamış. "
                "GEMINI_API_KEY eksik."
            )

        client = genai.Client(
            api_key=api_key
        )

        prompt = f"""
Sen MaviGPT'sin.

Kullanıcı Türkçe konuşuyor.
Her zaman Türkçe cevap ver.

Samimi, güvenli ve yardımcı ol.
Gereksiz yere uzun cevap verme.

Kullanıcının mesajı:

{mesaj}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print(
            "MAVİGPT HATASI:",
            repr(e)
        )

        return (
            "Üzgünüm, şu anda cevap oluştururken "
            "bir sorun oluştu."
        )


# ============================================================
# UYGULAMAYI ÇALIŞTIR
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5050
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
