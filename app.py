
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    mesaj = request.args.get("mesaj", "")

    if mesaj.lower() == "merhaba":
        cevap = "Merhaba! 😄"
    elif mesaj.lower() == "nasılsın":
        cevap = "İyiyim 🤖 Sen nasılsın?"
    elif mesaj == "":
        cevap = "Bir şey yaz 👇"
    else:
        cevap = "Bunu henüz bilmiyorum 😅"

    return f"""
    <html>
    <head>
        <title>BaharGPT</title>
        <style>
            body {{
                font-family: Arial;
                background: #343541;
                color: white;
                margin: 0;
                display: flex;
                justify-content: center;
            }}

            .container {{
                width: 600px;
                margin-top: 50px;
            }}

            h1 {{
                text-align: center;
                color: #10a37f;
            }}

            .chat {{
                background: #444654;
                padding: 15px;
                border-radius: 10px;
                margin-top: 10px;
            }}

            input {{
                width: 80%;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }}

            button {{
                padding: 10px;
                border: none;
                background: #10a37f;
                color: white;
                border-radius: 8px;
                cursor: pointer;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <h1>🤖 BaharGPT</h1>

            <form>
                <input name="mesaj" placeholder="Mesaj yaz...">
                <button>Gönder</button>
            </form>

            <div class="chat">
                <p><b>Sen:</b> {mesaj}</p>
                <p><b>BaharGPT:</b> {cevap}</p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
