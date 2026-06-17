
from flask import Flask, request
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    mesaj = request.args.get("mesaj")

    if not mesaj:
        return "Bir şey yaz 😊"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": mesaj}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Hata: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
