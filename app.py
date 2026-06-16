from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    mesaj = request.args.get("mesaj", "")

    if mesaj.lower() == "merhaba":
        cevap = "Merhaba! 😄"
    elif mesaj.lower() == "nasılsın":
        cevap = "İyiyim 🤖"
    elif mesaj == "":
        cevap = "Bir şey yaz 😊"
    else:
        cevap = "Bunu henüz bilmiyorum 😅"

    return f"""
    <h1>🤖 BaharGPT</h1>

    <form>
        <input name="mesaj" placeholder="Bir şey yaz">
        <button>Gönder</button>
    </form>

    <p><b>Sen:</b> {mesaj}</p>
    <p><b>AI:</b> {cevap}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
