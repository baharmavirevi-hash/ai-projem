import os
from flask import Flask, request, render_template
from google import genai

app = Flask(__name__)

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

# 🌊 MaviGPT
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
- Kod yazabiliyorsun.
- Derslerde yardımcı ol.
- Sohbet edebilirsin.

Kullanıcı:
{mesaj}
"""
            )

            cevap = response.text

        except Exception as e:
            cevap = str(e)

    return render_template("mavigpt.html", cevap=cevap)


# 🩺 Cebimdeki Doktor
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
- Doktor gibi kesin teşhis koyma.
- Olası nedenleri açıkla.
- Gerektiğinde doktora gitmesini öner.
- Acil durum belirtilerinde acil servise başvurmasını söyle.
- İlaç reçeteleme.
- Samimi ve anlaşılır ol.

Kullanıcı:
{mesaj}
"""
            )

            cevap = response.text

        except Exception as e:
            cevap = str(e)

    return render_template("doctor.html", cevap=cevap)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
