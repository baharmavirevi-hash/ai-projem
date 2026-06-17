from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home():
    mesaj = request.args.get("mesaj", "")

    if mesaj == "":
        cevap = "Bir şey yaz 😊"

    elif "merhaba" in mesaj.lower():
        cevap = "Merhaba Bahar! 😊"

    elif "nasılsın" in mesaj.lower():
        cevap = "Ben iyiyim 🌱 Sen nasılsın?"

    elif "adın ne" in mesaj.lower():
        cevap = "Ben BaharGPT'yim 😎"

    elif "kaç yaşındasın" in mesaj.lower():
        cevap = "Benim yaşım yok ama hep genç kalacağım 😄"

    else:
        cevap = f"'{mesaj}' yazdın. Henüz öğreniyorum 🌱"

    return render_template("index.html", cevap=cevap)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
