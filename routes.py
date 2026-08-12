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
# ROUTES
# ============================================================

def register_routes(app):

    # ========================================================
    # DATABASE
    # ========================================================

    try:
        init_db()
        print("DATABASE AKTİF")

    except Exception as e:
        print(
            "DATABASE BAŞLATMA HATASI:",
            repr(e)
        )


    # ========================================================
    # UPLOAD AYARLARI
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
    # FOTOĞRAF DOSYALARI
    # ========================================================

    @app.route(
        "/uploads/<filename>"
    )
    def uploaded_file(filename):

        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename
        )


    # ========================================================
    # 404
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
    # 500
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

        mesaj = ""
        cevap = ""
        filename = None


        # ----------------------------------------------------
        # SOHBETLER
        # ----------------------------------------------------

        try:

            sohbetler = get_chats(
                "normal"
            )

        except Exception as e:

            print(
                "SOHBET OKUMA HATASI:",
                repr(e)
            )

            sohbetler = []


        # ----------------------------------------------------
        # MESAJLAR
        # ----------------------------------------------------

        try:

            mesajlar = get_chat_messages(
                "normal"
            )

        except Exception as e:

            print(
                "MESAJ OKUMA HATASI:",
                repr(e)
            )

            mesajlar = []


        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                request.form.get(
                    "message",
                    ""
                )
            ).strip()


            # ------------------------------------------------
            # FOTOĞRAF
            # ------------------------------------------------

            foto = request.files.get(
                "photo"
            )

            if not foto:

                foto = request.files.get(
                    "foto"
                )


            # ------------------------------------------------
            # FOTOĞRAF KAYDET
            # ------------------------------------------------

            if foto and foto.filename:

                try:

                    filename = foto.filename

                    foto.save(
                        os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            filename
                        )
                    )

                except Exception as e:

                    print(
                        "FOTOĞRAF KAYIT HATASI:",
                        repr(e)
                    )

                    filename = None


            # ------------------------------------------------
            # MESAJ VARSA
            # ------------------------------------------------

            if mesaj:

                try:

                    # Bu fonksiyon app.py'de mevcutsa
                    # kullanılacak.
                    cevap = ask_mavigpt(
                        mesaj
                    )

                except NameError:

                    cevap = (
                        "MaviGPT bağlantısı henüz "
                        "ayarlanmadı."
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
                # KAYDET
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


                # ------------------------------------------------
                # LİSTEYİ YENİLE
                # ------------------------------------------------

                try:

                    mesajlar = get_chat_messages(
                        "normal"
                    )

                    sohbetler = get_chats(
                        "normal"
                    )

                except Exception as e:

                    print(
                        "SOHBET YENİLEME HATASI:",
                        repr(e)
                    )


        # ----------------------------------------------------
        # SAYFA
        # ----------------------------------------------------

        return render_template(
            "mavigpt.html",

            mesaj=mesaj,

            cevap=cevap,

            filename=filename,

            foto_url=(
                url_for(
                    "uploaded_file",
                    filename=filename
                )
                if filename
                else None
            ),

            mesajlar=mesajlar,

            sohbetler=sohbetler
        )


    # ========================================================
    # CHAT API
    # ========================================================

    @app.route(
        "/chat",
        methods=["POST"]
    )
    def chat_api():

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
                "error": (
                    "MaviGPT şu anda "
                    "cevap veremiyor."
                )
            }), 500


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


        return jsonify({
            "success": True,
            "message": message,
            "response": response
        })


    # ========================================================
    # MESAJLAR API
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
            }), 500


    # ========================================================
    # SOHBETLER API
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

            rows = get_chats(
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
    # SOHBET BAŞLIĞI DÜZENLE
    # ========================================================

    @app.route(
        "/chat/edit/<int:chat_id>",
        methods=["POST"]
    )
    def chat_edit(chat_id):

        data = request.get_json(
            silent=True
        )


        if data:

            title = data.get(
                "title",
                ""
            ).strip()

        else:

            title = request.form.get(
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


        try:

            kayitlar = get_health_records()

        except Exception as e:

            print(
                "SAĞLIK OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []


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


        try:

            kayitlar = get_period_records()

        except Exception as e:

            print(
                "REGL OKUMA HATASI:",
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


        if request.method == "POST":

            date = request.form.get(
                "date",
                ""
            ).strip()

            count_raw = request.form.get(
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

                count = max(
                    0,
                    int(count_raw or 0)
                )

            except (
                ValueError,
                TypeError
            ):

                count = 0


            if (
                date
                or count
                or condition
                or note
            ):

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


        try:

            kayitlar = get_diarrhea_records()

        except Exception as e:

            print(
                "SİNDİRİM OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []


        return render_template(
            "diarrhea.html",
            kayitlar=kayitlar,
            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # İLAÇ TAKİBİ
    # ========================================================

    @app.route(
        "/medicine",
        methods=["GET", "POST"]
    )
    def medicine():

        kayit_mesaji = None


        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            dose = request.form.get(
                "dose",
                ""
            ).strip()

            hour = request.form.get(
                "hour",
                ""
            ).strip()

            start_date = request.form.get(
                "start_date",
                ""
            ).strip()


            if name:

                try:

                    save_medicine(
                        name,
                        dose,
                        hour,
                        start_date
                    )

                    kayit_mesaji = (
                        "✅ İlaç kaydın kaydedildi."
                    )

                except Exception as e:

                    print(
                        "İLAÇ KAYIT HATASI:",
                        repr(e)
                    )

                    kayit_mesaji = (
                        "❌ İlaç kaydı kaydedilemedi."
                    )


        try:

            kayitlar = get_medicines()

        except Exception as e:

            print(
                "İLAÇ OKUMA HATASI:",
                repr(e)
            )

            kayitlar = []


        return render_template(
            "medicine.html",
            kayitlar=kayitlar,
            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # İLAÇ SİL
    # ========================================================

    @app.route(
        "/medicine/delete/<int:medicine_id>",
        methods=["POST", "DELETE"]
    )
    def medicine_delete(medicine_id):

        try:

            delete_medicine(
                medicine_id
            )

        except Exception as e:

            print(
                "İLAÇ SİLME HATASI:",
                repr(e)
            )


        return redirect(
            url_for("medicine")
        )


    # ========================================================
    # AYARLAR
    # ========================================================

    @app.route(
        "/settings",
        methods=["GET", "POST"]
    )
    def settings():

        kayit_mesaji = None


        if request.method == "POST":

            mode = request.form.get(
                "mode",
                "normal"
            ).strip()

            personality = request.form.get(
                "personality",
                "friendly"
            ).strip()


            try:

                save_settings(
                    mode,
                    personality
                )

                kayit_mesaji = (
                    "✅ Ayarların kaydedildi."
                )

            except Exception as e:

                print(
                    "AYAR KAYIT HATASI:",
                    repr(e)
                )

                kayit_mesaji = (
                    "❌ Ayarlar kaydedilemedi."
                )


        try:

            settings_data = get_settings()

        except Exception as e:

            print(
                "AYAR OKUMA HATASI:",
                repr(e)
            )

            settings_data = {
                "mode": "normal",
                "personality": "friendly"
            }


        return render_template(
            "settings.html",

            settings=settings_data,

            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # ARKADAŞLAR
    # ========================================================

    @app.route(
        "/friends",
        methods=["GET", "POST"]
    )
    def friends():

        error = None
        room = None
        room_code = ""


        if request.method == "POST":

            action = request.form.get(
                "action",
                ""
            ).strip()


            # ------------------------------------------------
            # ODA OLUŞTUR
            # ------------------------------------------------

            if action == "create":

                room_name = request.form.get(
                    "room_name",
                    "Arkadaş Sohbeti"
                ).strip()


                if not room_name:

                    room_name = "Arkadaş Sohbeti"


                try:

                    room_code = create_friend_room(
                        room_name
                    )


                    return redirect(
                        url_for(
                            "friend_room",
                            room_code=room_code
                        )
                    )


                except Exception as e:

                    print(
                        "ODA OLUŞTURMA HATASI:",
                        repr(e)
                    )

                    error = (
                        "Sohbet odası oluşturulamadı."
                    )


            # ------------------------------------------------
            # ODAYA KATIL
            # ------------------------------------------------

            elif action == "join":

                room_code = request.form.get(
                    "room_code",
                    ""
                ).strip().upper()


                if not room_code:

                    error = (
                        "Lütfen sohbet kodunu gir."
                    )

                else:

                    try:

                        room = get_friend_room(
                            room_code
                        )


                        if not room:

                            error = (
                                "Bu sohbet koduna ait "
                                "oda bulunamadı."
                            )

                        else:

                            return redirect(
                                url_for(
                                    "friend_room",
                                    room_code=room_code
                                )
                            )


                    except Exception as e:

                        print(
                            "ODA ARAMA HATASI:",
                            repr(e)
                        )

                        error = (
                            "Sohbet odası aranırken "
                            "bir hata oluştu."
                        )


        return render_template(
            "friends.html",

            room=room,

            room_code=room_code,

            error=error
        )


    # ========================================================
    # ARKADAŞ SOHBET ODASI
    # ========================================================

    @app.route(
        "/friends/<room_code>",
        methods=["GET", "POST"]
    )
    def friend_room(room_code):

        room_code = (
            room_code
            or ""
        ).strip().upper()


        try:

            room = get_friend_room(
                room_code
            )

        except Exception as e:

            print(
                "ODA OKUMA HATASI:",
                repr(e)
            )

            return redirect(
                url_for("friends")
            )


        if not room:

            return redirect(
                url_for("friends")
            )


        error = None


        # ----------------------------------------------------
        # MESAJ GÖNDER
        # ----------------------------------------------------

        if request.method == "POST":

            username = request.form.get(
                "username",
                ""
            ).strip()

            message = request.form.get(
                "message",
                ""
            ).strip()


            if not username:

                username = "Misafir"


            if message:

                try:

                    success = save_friend_message(
                        room_code,
                        username,
                        message
                    )


                    if not success:

                        error = (
                            "Mesaj gönderilemedi."
                        )


                except Exception as e:

                    print(
                        "ARKADAŞ MESAJI HATASI:",
                        repr(e)
                    )

                    error = (
                        "Mesaj gönderilirken "
                        "bir hata oluştu."
                    )


        # ----------------------------------------------------
        # MESAJLARI GETİR
        # ----------------------------------------------------

        try:

            messages = get_friend_messages(
                room_code
            )

        except Exception as e:

            print(
                "ARKADAŞ MESAJLARI HATASI:",
                repr(e)
            )

            messages = []

            error = (
                "Mesajlar yüklenemedi."
            )


        return render_template(
            "friend_room.html",

            room=room,

            room_code=room_code,

            messages=messages,

            error=error
        )


