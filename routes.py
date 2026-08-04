from flask import render_template, request

from ai import ask_mavigpt
from doctor import ask_doctor

from database import save_chat, get_chats


def register_routes(app):

    @app.route("/")
    def home():

        mesaj = request.args.get("mesaj", "")
        cevap = ""

        if mesaj:
            cevap = ask_mavigpt(mesaj)
            save_chat("mavigpt", mesaj, cevap)

        sohbetler = get_chats("mavigpt")

        return render_template(
            "mavigpt.html",
            cevap=cevap,
            sohbetler=sohbetler
        )


    @app.route("/doctor")
    def doctor():

        mesaj = request.args.get("mesaj", "")
        cevap = ""

        if mesaj:
            cevap = ask_doctor(mesaj)
            save_chat("doctor", mesaj, cevap)

        sohbetler = get_chats("doctor")

        return render_template(
            "doctor.html",
            cevap=cevap,
            sohbetler=sohbetler
        )
