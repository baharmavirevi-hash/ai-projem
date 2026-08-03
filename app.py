import os
from flask import Flask, request, render_template
from openai import OpenAI

app = Flask(__name__)

key = os.environ.get("XAI_API_KEY")

client = OpenAI(
    api_key=key,
    base_url="https://api.x.ai/v1"
)

@app.route("/")
def home():
    mesaj = request.args.get("mesaj", "")

    cevap = ""

    if not key:
        cevap = "❌ XAI_API_KEY bulunamadı!"
    elif mesaj:
        try:
            response = client.chat.completions.create(
                model="grok-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen MaviGPT'sin. Türkçe konuşan, samimi ve derslerde yardımcı olan bir yapay zekasın."
                    },
                    {
                        "role": "user",
                        "content": mesaj
                    }
                ]
            )

            cevap = response.choices[0].message.content

        except Exception as e:
            cevap = f"Hata: {e}"

    return render_template("index.html", cevap=cevap)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
