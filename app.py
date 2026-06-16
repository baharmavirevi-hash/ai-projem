
from flask import Flask, request
from openai import OpenAI
import os

app = Flask(__name__)

print("API KEY VAR MI?:", os.getenv("OPENAI_API_KEY"))

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.route("/")
def home():
    return "BAHAR TEST"

    if mesaj:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen yardımcı bir asistansın."},
                {"role": "user", "content": mesaj}
            ]
        )

        cevap = response.choices[0].message.content

    return f"""
    <html>
    <body style="font-family:Arial; background:#343541; color:white; text-align:center;">
        <h1>🤖 BaharGPT</h1>

        <form>
            <input name="mesaj" style="padding:10px; width:60%;">
            <button>Gönder</button>
        </form>

        <div style="margin-top:20px;">
            <p><b>Sen:</b> {mesaj}</p>
            <p><b>AI:</b> {cevap}</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
