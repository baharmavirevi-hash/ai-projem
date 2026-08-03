import os
from flask import Flask, request, render_template
from google import genai

app = Flask(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/")
def home():
    mesaj = request.args.get("mesaj", "")
    cevap = ""

    if mesaj:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Sen MaviGPT'sin.
Türkçe konuş.
Samimi ol.
Öğrencilere derslerinde yardımcı ol.
Cevaplarını anlaşılır yaz.

Kullanıcının mesajı:
{mesaj}
"""
            )

            cevap = response.text

        except Exception as e:
            cevap = f"Hata: {e}"

    return render_template("index.html", cevap=cevap)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
