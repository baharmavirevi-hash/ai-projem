
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

client = OpenAI()

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
    cevap = f"Hata oluştu: {e}"
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
