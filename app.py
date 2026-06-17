import os
from flask import Flask, request, render_template
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    mesaj = request.args.get("mesaj", "")

    cevap = "Bir şey yaz 😊"

    if mesaj:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sen yardımcı bir asistansın."},
                    {"role": "user", "content": mesaj}
                ]
            )
            cevap = response.choices[0].message.content
        except Exception as e:
            cevap = f"Hata: {e}"

    return render_template("index.html", cevap=cevap)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

