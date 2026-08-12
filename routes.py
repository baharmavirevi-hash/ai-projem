from flask import (
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    send_from_directory,
    current_app
)

import os
import uuid
import json
import time


# ============================================================
# DATABASE
# ============================================================

from database import (
    init_db,

    # MaviGPT
    save_chat,
    get_chat_messages,
    get_chats,
    get_chat,
    get_chat_by_id,
    update_chat_title,
    delete_chat,

    # Sağlık
    save_health_record,
    get_health_records,

    # Regl
    save_period_record,
    get_period_records,

    # Sindirim
    save_diarrhea_record,
    get_diarrhea_records,

    # İlaç
    save_medicine,
    get_medicines,
    delete_medicine,

    # Ayarlar
    get_settings,
    save_settings,

    # Arkadaş sistemi
    create_friend_room,
    get_friend_room,
    save_friend_message,
    get_friend_messages
)


# ============================================================
# GEÇİCİ GÖRÜNTÜLÜ KONUŞMA ODALARI
# ============================================================
#
# WebRTC bağlantısında tarayıcılar birbirleriyle bağlantı
# kurarken offer / answer / ICE bilgilerini paylaşır.
#
# Bu sözlük sunucu yeniden başlatılırsa temizlenir.
# Gerçek video sunucu üzerinden aktarılmaz.
#
# ============================================================

VIDEO_ROOMS = {}


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def get_upload_folder(app):

    folder = app.config.get(
        "UPLOAD_FOLDER"
    )

    if not folder:

        folder = os.path.join(
            app.root_path,
            "uploads"
        )

        app.config["UPLOAD_FOLDER"] = folder

    os.makedirs(
        folder,
        exist_ok=True
    )

    return folder


def save_uploaded_file(
    app,
    uploaded_file
):

    if not uploaded_file:
        return None

    if not uploaded_file.filename:
        return None

    original_name = uploaded_file.filename

    extension = os.path.splitext(
        original_name
    )[1].lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp"
    }

    if extension not in allowed_extensions:

        return None

    filename = (
        uuid.uuid4().hex
        + extension
    )

    folder = get_upload_folder(
        app
    )

    path = os.path.join(
        folder,
        filename
    )

    uploaded_file.save(
        path
    )

    return filename


def uploaded_url(
    filename
):

    if not filename:
        return None

    return url_for(
        "uploaded_file",
        filename=filename
    )


def row_to_dict(row):

    if row is None:
        return None

    try:

        return dict(row)

    except Exception:

        return row


def friend_messages_to_list(
    messages
):

    result = []

    for message in messages or []:

        try:

            item = dict(message)

        except Exception:

            item = {
                "message": str(message)
            }

        result.append(
            item
        )

    return result


# ============================================================
# MAVİGPT CEVAP FONKSİYONU
# ============================================================
#
# routes.py'nin app.py ile birbirine import olarak bağlanmasını
# engellemek için doğrudan app.py import etmiyoruz.
#
# app.py içinde:
#
#     app.config["MAVIGPT_FUNCTION"] = ask_mavigpt
#
# şeklinde tanımlanırsa onu kullanır.
#
# Eğer tanımlı değilse kullanıcıya güvenli bir hata mesajı döner.
#
# ============================================================

def call_mavigpt(
    message,
    photo_path=None,
    history=None
):

    function = current_app.config.get(
        "MAVIGPT_FUNCTION"
    )

    if function is None:

        return (
            "MaviGPT bağlantısı şu anda "
            "yapılandırılmamış."
        )

    try:

        if history is not None:

            try:

                return function(
                    message,
                    photo_path,
                    history
                )

            except TypeError:

                pass

        if photo_path is not None:

            try:

                return function(
                    message,
                    photo_path
                )

            except TypeError:

                pass

        return function(
            message
        )

    except Exception as e:

        print(
            "MAVİGPT HATASI:",
            repr(e)
        )

        return (
            "Üzgünüm, şu anda cevap "
            "oluştururken bir hata oluştu."
        )


# ============================================================
# ROUTES
# ============================================================

def register_routes(app):

    # ========================================================
    # DATABASE BAŞLAT
    # ========================================================

    try:

        init_db()

        print(
            "DATABASE AKTİF"
        )

    except Exception as e:

        print(
            "DATABASE BAŞLATMA HATASI:",
            repr(e)
        )


    # ========================================================
    # UPLOAD KLASÖRÜ
    # ========================================================

    app.config.setdefault(
        "UPLOAD_FOLDER",
        os.path.join(
            app.root_path,
            "uploads"
        )
    )

    get_upload_folder(
        app
    )


    # ========================================================
    # FOTOĞRAF DOSYASI
    # ========================================================

    @app.route(
        "/uploads/<path:filename>"
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

        try:

            return (
                render_template(
                    "404.html"
                ),
                404
            )

        except Exception:

            return (
                "Sayfa bulunamadı.",
                404
            )


    # ========================================================
    # 500
    # ========================================================

    @app.errorhandler(500)
    def internal_server_error(error):

        try:

            return (
                render_template(
                    "500.html"
                ),
                500
            )

        except Exception:

            return (
                "Sunucu hatası.",
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


            if foto and foto.filename:

                try:

                    filename = save_uploaded_file(
                        app,
                        foto
                    )

                except Exception as e:

                    print(
                        "FOTOĞRAF KAYIT HATASI:",
                        repr(e)
                    )

                    filename = None


            # ------------------------------------------------
            # MESAJ VEYA FOTOĞRAF
            # ------------------------------------------------

            if mesaj or filename:

                ai_mesaj = mesaj

                if not ai_mesaj:

                    ai_mesaj = (
                        "Bu fotoğrafı incele ve "
                        "genel, güvenli bilgi ver."
                    )


                # --------------------------------------------
                # GEÇMİŞ
                # --------------------------------------------

                try:

                    history = get_chat_messages(
                        "normal"
                    )

                except Exception:

                    history = []


                # --------------------------------------------
                # MAVİGPT
                # --------------------------------------------

                photo_path = None

                if filename:

                    photo_path = os.path.join(
                        app.config[
                            "UPLOAD_FOLDER"
                        ],
                        filename
                    )


                cevap = call_mavigpt(
                    ai_mesaj,
                    photo_path,
                    history
                )


                # --------------------------------------------
                # KAYDET
                # --------------------------------------------

                try:

                    save_chat(
                        "normal",
                        mesaj if mesaj else "Fotoğraf",
                        cevap
                    )

                except Exception as e:

                    print(
                        "SOHBET KAYIT HATASI:",
                        repr(e)
                    )


                # --------------------------------------------
                # YENİLE
                # --------------------------------------------

                try:

                    mesajlar = get_chat_messages(
                        "normal"
                    )

                    sohbetler = get_chats(
                        "normal"
                    )

                except Exception:

                    pass


        return render_template(
            "mavigpt.html",

            mesaj=mesaj,

            cevap=cevap,

            filename=filename,

            foto_url=uploaded_url(
                filename
            ),

            mesajlar=mesajlar,

            sohbetler=sohbetler
        )


    # ========================================================
    # MAVİGPT CHAT API
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

            history = get_chat_messages(
                "normal"
            )

        except Exception:

            history = []


        response = call_mavigpt(
            message,
            None,
            history
        )


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

            result = [
                row_to_dict(row)
                for row in rows
            ]

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

            result = [
                row_to_dict(row)
                for row in rows
            ]

            return jsonify({
                "success": True,
                "chats": result
            })

        except Exception as e:

            print(
                "SOHBETLER HATASI:",
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
                "chat": row_to_dict(
                    sohbet
                )
            })

        except Exception as e:

            print(
                "GEÇMİŞ HATASI:",
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
        mesaj = None
        cevap = None
        filename = None


        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

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


            # ----------------------------------------------
            # SAĞLIK KAYDI
            # ----------------------------------------------

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


            # ----------------------------------------------
            # FOTOĞRAF
            # ----------------------------------------------

            foto = request.files.get(
                "photo"
            )

            if foto and foto.filename:

                filename = save_uploaded_file(
                    app,
                    foto
                )


            # ----------------------------------------------
            # MAVİGPT
            # ----------------------------------------------

            if mesaj or filename:

                ai_mesaj = mesaj or (
                    "Bu sağlık fotoğrafı hakkında "
                    "genel ve güvenli bilgi ver. "
                    "Kesin tanı koyma."
                )

                photo_path = None

                if filename:

                    photo_path = os.path.join(
                        app.config[
                            "UPLOAD_FOLDER"
                        ],
                        filename
                    )

                cevap = call_mavigpt(
                    ai_mesaj,
                    photo_path
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

            mesaj=mesaj,

            cevap=cevap,

            kayitlar=kayitlar,

            kayit_mesaji=kayit_mesaji,

            foto_url=uploaded_url(
                filename
            )
        )


    # ========================================================
    # REGL
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
    # SİNDİRİM
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
                    int(
                        count_raw or 0
                    )
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
    # İLAÇ
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
        methods=["POST"]
    )
    def medicine_delete(
        medicine_id
    ):

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
            url_for(
                "medicine"
            )
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
    # ARKADAŞLAR ANA SAYFA
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

                    room_name = (
                        "Arkadaş Sohbeti"
                    )


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
                        "ARKADAŞ ODASI OLUŞTURMA HATASI:",
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
                            "ARKADAŞ ODASI ARAMA HATASI:",
                            repr(e)
                        )

                        error = (
                            "Sohbet odası bulunurken "
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
    def friend_room(
        room_code
    ):

        room_code = (
            room_code
            or ""
        ).strip().upper()


        # ----------------------------------------------------
        # ODAYI BUL
        # ----------------------------------------------------

        try:

            room = get_friend_room(
                room_code
            )

        except Exception as e:

            print(
                "ARKADAŞ ODASI OKUMA HATASI:",
                repr(e)
            )

            return redirect(
                url_for(
                    "friends"
                )
            )


        if not room:

            return redirect(
                url_for(
                    "friends"
                )
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
                        "ARKADAŞ MESAJI KAYIT HATASI:",
                        repr(e)
                    )

                    error = (
                        "Mesaj gönderilirken "
                        "bir hata oluştu."
                    )


        # ----------------------------------------------------
        # MESAJLAR
        # ----------------------------------------------------

        try:

            messages = get_friend_messages(
                room_code
            )

        except Exception as e:

            print(
                "ARKADAŞ MESAJLARI OKUMA HATASI:",
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


    # ========================================================
    # ARKADAŞ MESAJLARI API
    # ========================================================
    #
    # friend_room.html bunu belirli aralıklarla çağırarak
    # sayfayı tamamen yenilemeden yeni mesajları alabilir.
    #
    # ========================================================

    @app.route(
        "/friends/<room_code>/messages",
        methods=["GET"]
    )
    def friend_messages_api(
        room_code
    ):

        room_code = (
            room_code
            or ""
        ).strip().upper()


        try:

            room = get_friend_room(
                room_code
            )

            if not room:

                return jsonify({
                    "success": False,
                    "error": "Oda bulunamadı.",
                    "messages": []
                }), 404


            messages = get_friend_messages(
                room_code
            )


            return jsonify({
                "success": True,
                "messages": friend_messages_to_list(
                    messages
                )
            })


        except Exception as e:

            print(
                "ARKADAŞ MESAJ API HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "error": "Mesajlar alınamadı.",
                "messages": []
            }), 500


    # ========================================================
    # ARKADAŞ FOTOĞRAF YÜKLEME
    # ========================================================

    @app.route(
        "/friends/<room_code>/upload",
        methods=["POST"]
    )
    def friend_upload(
        room_code
    ):

        room_code = (
            room_code
            or ""
        ).strip().upper()


        try:

            room = get_friend_room(
                room_code
            )

            if not room:

                return jsonify({
                    "success": False,
                    "error": "Oda bulunamadı."
                }), 404


        except Exception as e:

            print(
                "ARKADAŞ ODA KONTROL HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "error": "Oda kontrol edilemedi."
            }), 500


        photo = request.files.get(
            "photo"
        )

        if not photo:

            photo = request.files.get(
                "foto"
            )


        if not photo or not photo.filename:

            return jsonify({
                "success": False,
                "error": "Fotoğraf seçilmedi."
            }), 400


        try:

            filename = save_uploaded_file(
                app,
                photo
            )


            if not filename:

                return jsonify({
                    "success": False,
                    "error": (
                        "Desteklenmeyen fotoğraf "
                        "formatı."
                    )
                }), 400


            photo_url = uploaded_url(
                filename
            )


            username = request.form.get(
                "username",
                "Misafir"
            ).strip()


            if not username:

                username = "Misafir"


            # Fotoğrafı arkadaş mesaj sisteminde
            # normal mesaj olarak URL ile kaydediyoruz.
            photo_message = (
                "📷 FOTOĞRAF|"
                + photo_url
            )


            save_friend_message(
                room_code,
                username,
                photo_message
            )


            return jsonify({
                "success": True,
                "url": photo_url
            })


        except Exception as e:

            print(
                "ARKADAŞ FOTOĞRAF HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "error": "Fotoğraf yüklenemedi."
            }), 500


    # ========================================================
    # GÖRÜNTÜLÜ KONUŞMA
    # ========================================================
    #
    # Bu bölüm WebRTC için SIGNALING sunar.
    #
    # Video görüntüsü Flask'a gelmez.
    # Tarayıcılar mümkün olduğunda birbirlerine doğrudan
    # WebRTC bağlantısı kurar.
    #
    # ========================================================


    # ========================================================
    # VIDEO ODASINI OLUŞTUR / KONTROL ET
    # ========================================================

    @app.route(
        "/friends/<room_code>/video",
        methods=["GET"]
    )
    def video_room(
        room_code
    ):

        room_code = (
            room_code
            or ""
        ).strip().upper()


        try:

            room = get_friend_room(
                room_code
            )

        except Exception:

            room = None


        if not room:

            return redirect(
                url_for(
                    "friends"
                )
            )


        if room_code not in VIDEO_ROOMS:

            VIDEO_ROOMS[
                room_code
            ] = {
                "offer": None,
                "answer": None,
                "candidates": [],
                "created_at": time.time()
            }


        return render_template(
            "friend_room.html",

            room=room,

            room_code=room_code,

            messages=[],

            video_mode=True
        )


    # ========================================================
    # VIDEO SIGNALING GET
    # ========================================================

    @app.route(
        "/friends/<room_code>/video/state",
        methods=["GET"]
    )
    def video_state(
        room_code
    ):

        room_code = (
            room_code
            or ""
        ).strip().upper()


        state = VIDEO_ROOMS.get(
            room_code
        )


        if not state:

            return jsonify({
                "success": True,
                "offer": None,
                "answer": None,
                "candidates": []
            })


        return jsonify({
            "success": True,
            "offer": state.get(
                "offer"
            ),
            "answer": state.get(
                "answer"
            ),
            "candidates": state.get(
                "candidates",
                []
            )
        })


    # ========================================================
    # VIDEO SIGNALING POST
    # ========================================================

    @app.route(
        "/friends/<room_code>/video/signal",
        methods=["POST"]
    )
    def video_signal(
        room_code
    ):

        room_code = (
            room_code
            or ""
        ).strip().upper()


        data = request.get_json(
            silent=True
        ) or {}


        signal_type = data.get(
            "type"
        )


        signal_data = data.get(
            "data"
        )


        if room_code not in VIDEO_ROOMS:

            VIDEO_ROOMS[
                room_code
            ] = {
                "offer": None,
                "answer": None,
                "candidates": [],
                "created_at": time.time()
            }


        state = VIDEO_ROOMS[
            room_code
        ]


        # ----------------------------------------------------
        # OFFER
        # ----------------------------------------------------

        if signal_type == "offer":

            state["offer"] = signal_data

            return jsonify({
                "success": True,
                "type": "offer"
            })


        # ----------------------------------------------------
        # ANSWER
        # ----------------------------------------------------

        if signal_type == "answer":

            state["answer"] = signal_data

            return jsonify({
                "success": True,
                "type": "answer"
            })


        # ----------------------------------------------------
        # ICE CANDIDATE
        # ----------------------------------------------------

        if signal_type == "candidate":

            if signal_data:

                state.setdefault(
                    "candidates",
                    []
                ).append(
                    signal_data
                )


            return jsonify({
                "success": True,
                "type": "candidate"
            })


        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        if signal_type == "reset":

            VIDEO_ROOMS[
                room_code
            ] = {
                "offer": None,
                "answer": None,
                "candidates": [],
                "created_at": time.time()
            }


            return jsonify({
                "success": True,
                "type": "reset"
            })


        return jsonify({
            "success": False,
            "error": "Geçersiz sinyal türü."
        }), 400


    # ========================================================
    # VIDEO ODASI TEMİZLE
    # ========================================================

    @app.route(
        "/friends/<room_code>/video/leave",
        methods=["POST"]
    )
    def video_leave(
        room_code
    ):

        room_code = (
            room_code
            or ""
        ).strip().upper()


        VIDEO_ROOMS.pop(
            room_code,
            None
        )


        return jsonify({
            "success": True
        })


    # ========================================================
    # ARKADAŞ SİSTEMİ TEST
    # ========================================================

    @app.route(
        "/api/friends/test",
        methods=["GET"]
    )
    def friends_test():

        return jsonify({
            "success": True,
            "message": "Arkadaş sistemi çalışıyor."
        })


    # ========================================================
    # VIDEO TEST
    # ========================================================

    @app.route(
        "/api/video/test",
        methods=["GET"]
    )
    def video_test():

        return jsonify({
            "success": True,
            "message": (
                "Görüntülü konuşma signaling "
                "sistemi çalışıyor."
            )
        })


    # ========================================================
    # ROUTES HAZIR
    # ========================================================

    print(
        "✅ TÜM ROUTES BAŞARIYLA KAYDEDİLDİ"
    )

