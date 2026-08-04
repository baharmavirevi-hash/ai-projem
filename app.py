import os
import sqlite3
from flask import Flask, request, render_template
from google import genai

app = Flask(__name__)

# -----------------------------
# Veritabanı
# -----------------------------
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            message TEXT,
            answer TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Gemini
# -----------------------------
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

# -----------------------------
# MaviGPT
# -----------------------------
@app.route("/")
def mavigpt():

    mesaj = request.args.get("mesaj", "")
    cevap = ""

    if mesaj:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Sen MaviGPT'sin.

Kurallar:
- Türkçe konuş.
- Samimi ol.
- Kod yaz.
- Derslerde yardımcı ol.
- Sohbet et.

Kullanıcı:
{mesaj}
"""
            )

            cevap = response.text

            conn = sqlite3.connect("chat.db")
            c = conn.cursor()

            c.execute(
                "INSERT INTO chats(title, message, answer) VALUES (?, ?, ?)",
                (mesaj[:30], mesaj, cevap)
            )

            conn.commit()
            conn.close()

        except Exception as e:
            cevap = str(e)

    return render_template(
        "mavigpt.html",
        cevap=cevap
    )

# -----------------------------
# Cebimdeki Doktor
# -----------------------------
@app.route("/doctor")
def doctor():

    mesaj = request.args.get("mesaj", "")
    cevap = ""

    if mesaj:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Sen Cebimdeki Doktor adlı sağlık asistanısın.

Kurallar:
- Türkçe konuş.
- Kesin teşhis koyma.
- Olası nedenleri açıkla.
- Gerektiğinde doktora gitmesini öner.
- Acil belirtilerde acil servise yönlendir.
- İlaç reçetelemeden bilgi ver.
- Samimi ol.

Kullanıcı:
{mesaj}
"""
            )

            cevap = response.text

            conn = sqlite3.connect("chat.db")
            c = conn.cursor()

            c.execute(
                "INSERT INTO chats(title, message, answer) VALUES (?, ?, ?)",
                (mesaj[:30], mesaj, cevap)
            )

            conn.commit()
            conn.close()

        except Exception as e:
            cevap = str(e)

    return render_template(
        "doctor.html",
        cevap=cevap
    )

# -----------------------------
# Çalıştır
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
