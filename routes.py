from flask import (
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    send_from_directory
)

import os

from database import (
    init_db,
    save_chat,
    get_chat_messages,
    get_chats,
    get_chat,
    get_chat_by_id,
    update_chat_title,
    delete_chat,

    save_health_record,
    get_health_records,

    save_period_record,
    get_period_records,

    save_diarrhea_record,
    get_diarrhea_records,

    save_medicine,
    get_medicines,
    delete_medicine,

    get_settings,
    save_settings,

    create_friend_room,
    get_friend_room,
    save_friend_message,
    get_friend_messages
)


# ============================================================
# ROUTES KAYIT SİSTEMİ
# ============================================================

def register_routes(app):

    # ========================================================
    # DATABASE
    # ========================================================

    try:

        init_db()

    except Exception as e:

        print(
            "DATABASE BAŞLATMA HATASI:",
            repr(e)
        )


    # ========================================================
    # TEMEL AYARLAR
    # ========================================================

    app.config.setdefault(
        "UPLOAD_FOLDER",
        os.path.join(
            app.root_path,
            "uploads"
        )
    )

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )
    # ========================================================
    # 404 SAYFASI
    # ========================================================

    @app.errorhandler(404)
    def page_not_found(error):

        return (
            render_template(
                "404.html"
            ),
            404
        )


    # ========================================================
    # 500 SAYFASI
    # ========================================================

    @app.errorhandler(500)
    def internal_server_error(error):

        return (
            render_template(
                "500.html"
            ),
            500
        )


    # ========================================================
    # ANA SAYFA / MAVİGPT
    # ========================================================

    @app.route(
        "/",
        methods=["GET", "POST"]
    )
    def home():
============================
    # ANA SAYFA / MAVİGPT
    # ========================================================

    @app.route(
        "/",
        methods=["GET", "POST"]
    )
    def home():

        mesaj = ""
        cevap = ""
        filename = None

        # ----------------------------------------------------
        # SOHBETLERİ GETİR
        # ----------------------------------------------------

        try:

            sohbetler = get_chats(
                "normal"
            )

        except Exception as e:

            print(
                "SOHBETLERİ GETİRME HATASI:",
                repr(e)
            )

            sohbetler = []

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            mesaj = request.form.get(
                "message",
                ""
            ).strip()

            if mesaj:

                try:

                    # MaviGPT cevabı
                    cevap = ask_mavigpt(
                        mesaj
                    )

                except Exception as e:

                    print(
                        "MAVİGPT HATASI:",
                        repr(e)
                    )

                    cevap = (
                        "Üzgünüm, şu anda "
                        "bir hata oluştu."
                    )

                # ------------------------------------------------
                # SOHBETİ KAYDET
                # ------------------------------------------------

                try:

                    save_chat(
                        "normal",
                        mesaj,
                        cevap
                    )

                except Exception as e:

                    print(
                        "SOHBET KAYIT HATASI:",
                        repr(e)
                    )

        # ----------------------------------------------------
        # SAYFAYI GÖSTER
        # ----------------------------------------------------

        return render_template(
            "index.html",

            mesaj=mesaj,

            cevap=cevap,

            filename=filename,

            sohbetler=sohbetler
        )
                "500.html"
            ),
            500
        )    # ========================================================
    # MAVİGPT CHAT API
    # ========================================================

    @app.route(
        "/chat",
        methods=["POST"]
    )
    def chat():

        data = request.get_json(
            silent=True
        ) or {}

        message = data.get(
            "message",
            ""
        ).strip()

        if not message:

            return jsonify({
                "success": False,
                "error": "Mesaj boş olamaz."
            }), 400

        # ----------------------------------------------------
        # MAVİGPT CEVABI
        # ----------------------------------------------------

        try:

            response = ask_mavigpt(
                message
            )

        except Exception as e:

            print(
                "CHAT API HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "error": "MaviGPT şu anda cevap veremiyor."
            }), 500

        # ----------------------------------------------------
        # DATABASE'E KAYDET
        # ----------------------------------------------------

        try:

            save_chat(
                "normal",
                message,
                response
            )

        except Exception as e:

            print(
                "CHAT KAYIT HATASI:",
                repr(e)
            )

        # ----------------------------------------------------
        # CEVAP
        # ----------------------------------------------------

        return jsonify({
            "success": True,
            "message": message,
            "response": response
        })


    # ========================================================
    # SOHBET MESAJLARI
    # ========================================================

    @app.route(
        "/messages",
        methods=["GET"]
    )
    def messages():

        chat_type = request.args.get(
            "chat_type",
            "normal"
        ).strip()

        try:

            rows = get_chat_messages(
                chat_type
            )

            result = []

            for row in rows:

                result.append({
                    "id": row["id"],
                    "chat_type": row["chat_type"],
                    "message": row["message"],
                    "response": row["response"],
                    "created_at": row["created_at"]
                })

            return jsonify({
                "success": True,
                "messages": result
            })

        except Exception as e:

            print(
                "MESAJLARI GETİRME HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "messages": []
            }), 500    # ========================================================
    # SOHBETLER
    # ========================================================

    @app.route(
        "/chats",
        methods=["GET"]
    )
    def chats():

        chat_type = request.args.get(
            "chat_type",
            "normal"
        ).strip()

        try:

            sohbetler = get_chats(
                chat_type
            )

            result = []

            for row in sohbetler:

                result.append({
                    "id": row["id"],
                    "chat_type": row["chat_type"],
                    "message": row["message"],
                    "response": row["response"],
                    "created_at": row["created_at"]
                })

            return jsonify({
                "success": True,
                "chats": result
            })

        except Exception as e:

            print(
                "SOHBETLERİ GETİRME HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "chats": []
            }), 500


    # ========================================================
    # TEK SOHBET
    # ========================================================

    @app.route(
        "/history/<int:chat_id>",
        methods=["GET"]
    )
    def history(chat_id):

        try:

            sohbet = get_chat(
                chat_id
            )

            if not sohbet:

                return jsonify({
                    "success": False,
                    "error": "Sohbet bulunamadı."
                }), 404

            return jsonify({
                "success": True,
                "chat": {
                    "id": sohbet["id"],
                    "chat_type": sohbet["chat_type"],
                    "message": sohbet["message"],
                    "response": sohbet["response"],
                    "created_at": sohbet["created_at"]
                }
            })

        except Exception as e:

            print(
                "SOHBET GEÇMİŞİ HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "error": "Sohbet yüklenemedi."
            }), 500


    # ========================================================
    # SOHBET DÜZENLE
    # ========================================================

    @app.route(
        "/chat/edit/<int:chat_id>",
        methods=["POST"]
    )
    def chat_edit(chat_id):

        data = request.get_json(
            silent=True
        ) or {}

        title = data.get(
            "title",
            ""
        ).strip()

        if not title:

            return jsonify({
                "success": False,
                "error": "Başlık boş olamaz."
            }), 400

        try:

            update_chat_title(
                chat_id,
                title
            )

            return jsonify({
                "success": True
            })

        except Exception as e:

            print(
                "SOHBET DÜZENLEME HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "error": "Sohbet düzenlenemedi."
            }), 500


    # ========================================================
    # SOHBET SİL
    # ========================================================

    @app.route(
        "/chat/delete/<int:chat_id>",
        methods=["POST", "DELETE"]
    )
    def chat_delete(chat_id):

        try:

            delete_chat(
                chat_id
            )

            return jsonify({
                "success": True
            })

        except Exception as e:

            print(
                "SOHBET SİLME HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "error": "Sohbet silinemedi."
            }), 500
                # ========================================================
    # CEBİMDEKİ DOKTOR
    # ========================================================

    @app.route(
        "/doctor",
        methods=["GET", "POST"]
    )
    def doctor():

        kayit_mesaji = None

        # ----------------------------------------------------
        # YENİ SAĞLIK KAYDI
        # ----------------------------------------------------

        if request.method == "POST":

            symptom = request.form.get(
                "symptom",
                ""
            ).strip()

            medicine = request.form.get(
                "medicine",
                ""
            ).strip()

            note = request.form.get(
                "note",
                ""
            ).strip()

            if symptom or medicine or note:

                try:

                    save_health_record(
                        symptom,
                        medicine,
                        note
                    )

                    kayit_mesaji = (
                        "✅ Sağlık kaydın kaydedildi."
                    )

                except Exception as e:

                    print(
                        "SAĞLIK KAYIT HATASI:",
                        repr(e)
                    )

                    kayit_mesaji = (
                        "❌ Sağlık kaydı kaydedilemedi."
                    )

        # ----------------------------------------------------
        # KAYITLARI GETİR
        # ----------------------------------------------------

        try:

            kayitlar = get_health_records()

        except Exception as e:

            print(
                "SAĞLIK KAYITLARI OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        # ----------------------------------------------------
        # SAYFAYI GÖSTER
        # ----------------------------------------------------

        return render_template(
            "doctor.html",

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # REGL TAKİBİ
    # ========================================================

    @app.route(
        "/period",
        methods=["GET", "POST"]
    )
    def period():

        kayit_mesaji = None

        # ----------------------------------------------------
        # KAYIT
        # ----------------------------------------------------

        if request.method == "POST":

            start_date = request.form.get(
                "start_date",
                ""
            ).strip()

            end_date = request.form.get(
                "end_date",
                ""
            ).strip()

            note = request.form.get(
                "note",
                ""
            ).strip()

            if start_date:

                try:

                    save_period_record(
                        start_date,
                        end_date,
                        note
                    )

                    kayit_mesaji = (
                        "✅ Regl kaydın kaydedildi."
                    )

                except Exception as e:

                    print(
                        "REGL KAYIT HATASI:",
                        repr(e)
                    )

                    kayit_mesaji = (
                        "❌ Regl kaydı kaydedilemedi."
                    )

        # ----------------------------------------------------
        # KAYITLARI GETİR
        # ----------------------------------------------------

        try:

            kayitlar = get_period_records()

        except Exception as e:

            print(
                "REGL KAYITLARI OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "period.html",

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # SİNDİRİM TAKİBİ
    # ========================================================

    @app.route(
        "/diarrhea",
        methods=["GET", "POST"]
    )
    def diarrhea():

        kayit_mesaji = None

        # ----------------------------------------------------
        # KAYIT
        # ----------------------------------------------------

        if request.method == "POST":

            date = request.form.get(
                "date",
                ""
            ).strip()

            count = request.form.get(
                "count",
                "0"
            ).strip()

            condition = request.form.get(
                "condition",
                ""
            ).strip()

            note = request.form.get(
                "note",
                ""
            ).strip()

            try:

                count = int(
                    count or 0
                )

            except ValueError:

                count = 0

            if date:

                try:

                    save_diarrhea_record(
                        date,
                        count,
                        condition,
                        note
                    )

                    kayit_mesaji = (
                        "✅ Sindirim kaydın kaydedildi."
                    )

                except Exception as e:

                    print(
                        "SİNDİRİM KAYIT HATASI:",
                        repr(e)
                    )

                    kayit_mesaji = (
                        "❌ Sindirim kaydı kaydedilemedi."
                    )

        # ----------------------------------------------------
        # KAYITLARI GETİR
        # ----------------------------------------------------

        try:

            kayitlar = get_diarrhea_records()

        except Exception as e:

            print(
                "SİNDİRİM KAYITLARI OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "diarrhea.html",

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji
        )
            

