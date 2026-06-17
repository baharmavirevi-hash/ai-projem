
from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    mesaj = request.args.get("mesaj", "")

    if not mesaj:
        return "Bir şey yaz 😊"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen yardımcı bir asistansın."},
                {"role": "user", "content": mesaj}
            ]
        )

        return jsonify({
            "cevap": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"hata": str(e)})
