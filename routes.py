import os
import uuid
from functools import wraps

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
    send_from_directory
)

from database import (
    # ============================================================
    # KULLANICI
    # ============================================================
    create_user,
    get_user_by_username,
    get_user_by_id,
    check_user_password,

    # ============================================================
    # MAVİGPT
    # ============================================================
    save_chat,
    get_chat_messages,
    get_chats,
    get_chat,
    get_chat_by_id,
    update_chat_title,
    delete_chat,

    # ============================================================
    # SAĞLIK
    # ============================================================
    save_health_record,
    get_health_records,

    # ============================================================
    # REGL
    # ============================================================
    save_period_record,
    get_period_records,

    # ============================================================
    # SİNDİRİM
    # ============================================================
    save_diarrhea_record,
    get_diarrhea_records,

    # ============================================================
    # İLAÇ
    # ============================================================
    save_medicine,
    get_medicines,
    delete_medicine,

    # ============================================================
    # AYARLAR
    # ============================================================
    save_settings,
    get_settings,

    # ============================================================
    # ARKADAŞLIK
    # ============================================================
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    get_friends,
    get_pending_friend_requests,
    are_friends,

    # ============================================================
    # ARKADAŞ ODALARI
    # ============================================================
    create_friend_room,
    get_friend_room,
    join_friend_room,
    is_room_member,
    get_friend_room_members,
    save_friend_message,
    save_friend_photo_message,
    get_friend_messages,
    delete_friend_room,
    get_user_friend_rooms,

    # ============================================================
    # PUSH BİLDİRİM
    # ============================================================
    save_push_subscription,
    get_push_subscriptions,
    delete_push_subscription
)


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def current_user():
    """
    Oturum açmış kullanıcının bilgilerini döndürür.
    """

    user_id = session.get("user_id")

    if not user_id:
        return None

    return get_user_by_id(user_id)


def login_required(view):
    """
    Giriş yapılmadan erişilmemesi gereken sayfalar için decorator.
    """

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if not session.get("user_id"):
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view


def safe_int(value, default=0):
    """
    Güvenli integer dönüşümü.
    """

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# ROUTE KAYIT SİSTEMİ
# ============================================================

def register_routes(app):

    # ========================================================
    # ANA SAYFA
    # ========================================================

    @app.route("/")
    def home():

        user = current_user()

        return render_template(
            "index.html",
            user=user
        )

    # ========================================================
    # MAVİGPT
    # ========================================================

    @app.route("/mavigpt")
    @app.route("/chat")
    @login_required
    def mavigpt():

        messages = get_chat_messages("normal")

        return render_template(
            "mavigpt.html",
            messages=messages,
            user=current_user()
        )

    # ========================================================
    # MAVİGPT MESAJ GÖNDER
    # ========================================================

    @app.route("/send", methods=["POST"])
    @login_required
    def send_message():

        try:

            data = request.get_json(silent=True)

            if data is None:
                data = request.form

            message = (
                data.get("message")
                or data.get("text")
                or ""
            ).strip()

            if not message:

                return jsonify({
                    "success": False,
                    "error": "Mesaj boş olamaz."
                }), 400

            from app import ask_mavigpt

            response = ask_mavigpt(message)

            save_chat(
                "normal",
                message,
                response
            )

            return jsonify({
                "success": True,
                "message": message,
                "response": response
            })

        except Exception as e:

            print(
                "SEND HATASI:",
                repr(e)
            )

            return jsonify({
                "success": False,
                "error": "Mesaj gönderilirken bir hata oluştu."
            }), 500

    # ========================================================
    # CHAT MESAJLARI
    # ========================================================

    @app.route("/messages")
    @login_required
    def messages():

        chat_type = request.args.get(
            "chat_type",
            "normal"
        )

        rows = get_chat_messages(chat_type)

        return jsonify([
            dict(row)
            for row in rows
        ])

    # ========================================================
    # SOHBETLER
    # ========================================================

    @app.route("/chats")
    @login_required
    def chats():

        chat_type = request.args.get(
            "chat_type",
            "normal"
        )

        rows = get_chats(chat_type)

        return jsonify([
            dict(row)
            for row in rows
        ])

    # ========================================================
    # CHAT HISTORY
    # ========================================================

    @app.route("/history")
    @login_required
    def history():

        chat_type = request.args.get(
            "chat_type",
            "normal"
        )

        rows = get_chat_messages(chat_type)

        return render_template(
            "mavigpt.html",
            messages=rows,
            user=current_user()
        )

    # ========================================================
    # TEK SOHBET
    # ========================================================

    @app.route("/chat/<int:chat_id>")
    @login_required
    def single_chat(chat_id):

        chat = get_chat(chat_id)

        if not chat:

            return jsonify({
                "success": False,
                "error": "Sohbet bulunamadı."
            }), 404

        return jsonify(
            dict(chat)
        )

    # ========================================================
    # SOHBET BAŞLIĞI
    # ========================================================

    @app.route(
        "/chat/<int:chat_id>/title",
        methods=["POST"]
    )
    @login_required
    def edit_chat_title(chat_id):

        data = request.get_json(
            silent=True
        ) or request.form

        title = (
            data.get("title")
            or ""
        ).strip()

        if not title:

            return jsonify({
                "success": False,
                "error": "Başlık boş olamaz."
            }), 400

        chat = get_chat(chat_id)

        if not chat:

            return jsonify({
                "success": False,
                "error": "Sohbet bulunamadı."
            }), 404

        update_chat_title(
            chat_id,
            title
        )

        return jsonify({
            "success": True
        })

    # ========================================================
    # SOHBET SİL
    # ========================================================

    @app.route(
        "/chat/<int:chat_id>/delete",
        methods=["POST", "DELETE"]
    )
    @login_required
    def remove_chat(chat_id):

        chat = get_chat(chat_id)

        if not chat:

            return jsonify({
                "success": False,
                "error": "Sohbet bulunamadı."
            }), 404

        delete_chat(chat_id)

        return jsonify({
            "success": True
        })

    # ========================================================
    # GİRİŞ
    # ========================================================

    @app.route(
        "/login",
        methods=["GET", "POST"]
    )
    def login():

        if session.get("user_id"):

            return redirect(
                url_for("home")
            )

        if request.method == "POST":

            username = (
                request.form.get("username")
                or ""
            ).strip()

            password = (
                request.form.get("password")
                or ""
            )

            if not username or not password:

                flash(
                    "Kullanıcı adı ve şifre gerekli.",
                    "error"
                )

                return render_template(
                    "login.html"
                )

            user = check_user_password(
                username,
                password
            )

            if user:

                session.clear()

                session["user_id"] = user["id"]

                session["username"] = user["username"]

                session["display_name"] = (
                    user["display_name"]
                    or user["username"]
                )

                return redirect(
                    url_for("home")
                )

            flash(
                "Kullanıcı adı veya şifre hatalı.",
                "error"
            )

        return render_template(
            "login.html"
        )

    # ========================================================
    # KAYIT
    # ========================================================

    @app.route(
        "/register",
        methods=["GET", "POST"]
    )
    def register():

        if session.get("user_id"):

            return redirect(
                url_for("home")
            )

        if request.method == "POST":

            username = (
                request.form.get("username")
                or ""
            ).strip()

            password = (
                request.form.get("password")
                or ""
            )

            display_name = (
                request.form.get("display_name")
                or ""
            ).strip()

            if not username or not password:

                flash(
                    "Kullanıcı adı ve şifre gerekli.",
                    "error"
                )

                return render_template(
                    "register.html"
                )

            if len(username) < 3:

                flash(
                    "Kullanıcı adı en az 3 karakter olmalı.",
                    "error"
                )

                return render_template(
                    "register.html"
                )

            if len(password) < 4:

                flash(
                    "Şifre en az 4 karakter olmalı.",
                    "error"
                )

                return render_template(
                    "register.html"
                )

            user_id = create_user(
                username=username,
                password=password,
                display_name=display_name or username
            )

            if not user_id:

                flash(
                    "Bu kullanıcı adı zaten kullanılıyor.",
                    "error"
                )

                return render_template(
                    "register.html"
                )

            session.clear()

            session["user_id"] = user_id

            session["username"] = username

            session["display_name"] = (
                display_name
                or username
            )

            return redirect(
                url_for("home")
            )

        return render_template(
            "register.html"
        )

    # ========================================================
    # ÇIKIŞ
    # ========================================================

    @app.route("/logout")
    def logout():

        session.clear()

        return redirect(
            url_for("login")
        )

    # ========================================================
    # PROFİL
    # ========================================================

    @app.route("/profile")
    @login_required
    def profile():

        user = current_user()

        return render_template(
            "profile.html",
            user=user
        )

    # ========================================================
    # SAĞLIK / CEBİMDEKİ DOKTOR
    # ========================================================

    @app.route("/doctor")
    @app.route("/cebimdeki-doktor")
    @login_required
    def doctor():

        records = get_health_records()

        return render_template(
            "doctor.html",
            records=records,
            health_records=records,
            user=current_user()
        )

    # ========================================================
    # SAĞLIK KAYDI
    # ========================================================

    @app.route(
        "/doctor/save",
        methods=["POST"]
    )
    @login_required
    def save_doctor_record():

        symptom = (
            request.form.get("symptom")
            or ""
        ).strip()

        medicine = (
            request.form.get("medicine")
            or ""
        ).strip()

        note = (
            request.form.get("note")
            or ""
        ).strip()

        save_health_record(
            symptom,
            medicine,
            note
        )

        return redirect(
            url_for("doctor")
        )

    # ========================================================
    # SAĞLIK KAYITLARI API
    # ========================================================

    @app.route("/health-records")
    @login_required
    def health_records_api():

        rows = get_health_records()

        return jsonify([
            dict(row)
            for row in rows
        ])

    # ========================================================
    # REGL TAKİBİ
    # ========================================================

    @app.route("/period")
    @app.route("/regl")
    @app.route("/period-tracker")
    @login_required
    def period():

        records = get_period_records()

        return render_template(
            "period.html",
            records=records,
            period_records=records,
            user=current_user()
        )

    # ========================================================
    # REGL KAYDET
    # ========================================================

    @app.route(
        "/period/save",
        methods=["POST"]
    )
    @app.route(
        "/regl/save",
        methods=["POST"]
    )
    @login_required
    def save_period():

        start_date = (
            request.form.get("start_date")
            or ""
        ).strip()

        end_date = (
            request.form.get("end_date")
            or ""
        ).strip()

        note = (
            request.form.get("note")
            or ""
        ).strip()

        save_period_record(
            start_date,
            end_date,
            note
        )

        return redirect(
            url_for("period")
        )

    # ========================================================
    # SİNDİRİM TAKİBİ
    # ========================================================

    @app.route("/diarrhea")
    @app.route("/digestive")
    @app.route("/sindirim")
    @app.route("/diarrhea-tracker")
    @login_required
    def diarrhea():

        records = get_diarrhea_records()

        return render_template(
            "diarrhea.html",
            records=records,
            diarrhea_records=records,
            user=current_user()
        )

    # ========================================================
    # SİNDİRİM KAYDET
    # ========================================================

    @app.route(
        "/diarrhea/save",
        methods=["POST"]
    )
    @app.route(
        "/sindirim/save",
        methods=["POST"]
    )
    @login_required
    def save_diarrhea():

        date = (
            request.form.get("date")
            or ""
        ).strip()

        count = safe_int(
            request.form.get("count"),
            0
        )

        condition = (
            request.form.get("condition")
            or ""
        ).strip()

        note = (
            request.form.get("note")
            or ""
        ).strip()

        save_diarrhea_record(
            date,
            count,
            condition,
            note
        )

        return redirect(
            url_for("diarrhea")
        )

    # ========================================================
    # İLAÇLAR
    # ========================================================

    @app.route("/medicine")
    @app.route("/medicines")
    @app.route("/ilaclar")
    @login_required
    def medicine():

        medicines = get_medicines()

        return render_template(
            "medicine.html",
            medicines=medicines,
            user=current_user()
        )

    # ========================================================
    # İLAÇ KAYDET
    # ========================================================

    @app.route(
        "/medicine/save",
        methods=["POST"]
    )
    @app.route(
        "/medicines/save",
        methods=["POST"]
    )
    @login_required
    def save_medicine_route():

        name = (
            request.form.get("name")
            or ""
        ).strip()

        dose = (
            request.form.get("dose")
            or ""
        ).strip()

        hour = (
            request.form.get("hour")
            or ""
        ).strip()

        start_date = (
            request.form.get("start_date")
            or ""
        ).strip()

        if not name:

            flash(
                "İlaç adı gerekli.",
                "error"
            )

            return redirect(
                url_for("medicine")
            )

        save_medicine(
            name,
            dose,
            hour,
            start_date
        )

        return redirect(
            url_for("medicine")
        )

    # ========================================================
    # İLAÇ SİL
    # ========================================================

    @app.route(
        "/medicine/delete/<int:medicine_id>",
        methods=["POST", "DELETE"]
    )
    @app.route(
        "/medicines/delete/<int:medicine_id>",
        methods=["POST", "DELETE"]
    )
    @login_required
    def remove_medicine(medicine_id):

        delete_medicine(
            medicine_id
        )

        if request.is_json:

            return jsonify({
                "success": True
            })

        return redirect(
            url_for("medicine")
        )

    # ========================================================
    # AYARLAR
    # ========================================================

    @app.route("/settings")
    @login_required
    def settings():

        settings_data = get_settings()

        return render_template(
            "settings.html",
            settings=settings_data,
            user=current_user()
        )

    # ========================================================
    # AYARLARI KAYDET
    # ========================================================

    @app.route(
        "/settings/save",
        methods=["POST"]
    )
    @login_required
    def save_settings_route():

        mode = (
            request.form.get("mode")
            or "normal"
        ).strip()

        personality = (
            request.form.get("personality")
            or "friendly"
        ).strip()

        save_settings(
            mode,
            personality
        )

        return redirect(
            url_for("settings")
        )

    # ========================================================
    # ========================================================
    # ARKADAŞ SİSTEMİ
    # ========================================================
    # ========================================================

    # ========================================================
    # ARKADAŞLAR SAYFASI
    # ========================================================

    @app.route("/friends")
    @login_required
    def friends():

        user_id = session["user_id"]

        friends_list = get_friends(
            user_id
        )

        pending_requests = (
            get_pending_friend_requests(
                user_id
            )
        )

        rooms = get_user_friend_rooms(
            user_id
        )

        return render_template(
            "friends.html",
            friends=friends_list,
            pending_friend_requests=pending_requests,
            pending_requests=pending_requests,
            requests=pending_requests,
            rooms=rooms,
            user=current_user()
        )

    # ========================================================
    # KULLANICI ARA
    # ========================================================

    @app.route("/friends/search")
    @login_required
    def search_friends():

        username = (
            request.args.get("username")
            or request.args.get("q")
            or ""
        ).strip()

        if not username:

            return jsonify({
                "success": True,
                "users": []
            })

        user_id = session["user_id"]

        user = get_user_by_username(
            username
        )

        if not user:

            return jsonify({
                "success": True,
                "users": []
            })

        if user["id"] == user_id:

            return jsonify({
                "success": True,
                "users": []
            })

        return jsonify({
            "success": True,
            "users": [{
                "id": user["id"],
                "username": user["username"],
                "display_name": (
                    user["display_name"]
                    or user["username"]
                )
            }]
        })

    # ========================================================
    # ARKADAŞLIK İSTEĞİ GÖNDER
    # ========================================================

    @app.route(
        "/friends/request",
        methods=["POST"]
    )
    @login_required
    def friend_request():

        data = request.get_json(
            silent=True
        ) or request.form

        receiver_id = safe_int(
            data.get("receiver_id")
            or data.get("user_id")
        )

        if not receiver_id:

            return jsonify({
                "success": False,
                "error": "Kullanıcı bulunamadı."
            }), 400

        success = send_friend_request(
            session["user_id"],
            receiver_id
        )

        if not success:

            return jsonify({
                "success": False,
                "error": (
                    "Arkadaşlık isteği gönderilemedi. "
                    "Zaten arkadaş olabilirsiniz veya "
                    "bekleyen bir istek olabilir."
                )
            }), 400

        return jsonify({
            "success": True
        })

    # ========================================================
    # ARKADAŞLIK İSTEĞİ KABUL
    # ========================================================

    @app.route(
        "/friends/request/<int:request_id>/accept",
        methods=["POST"]
    )
    @login_required
    def accept_friend(request_id):

        success = accept_friend_request(
            request_id,
            session["user_id"]
        )

        return jsonify({
            "success": success
        })

    # ========================================================
    # ARKADAŞLIK İSTEĞİ REDDET
    # ========================================================

    @app.route(
        "/friends/request/<int:request_id>/reject",
        methods=["POST"]
    )
    @login_required
    def reject_friend(request_id):

        success = reject_friend_request(
            request_id,
            session["user_id"]
        )

        return jsonify({
            "success": success
        })

    # ========================================================
    # ARKADAŞLARI API
    # ========================================================

    @app.route("/api/friends")
    @login_required
    def friends_api():

        rows = get_friends(
            session["user_id"]
        )

        return jsonify([
            {
                "id": row["id"],
                "username": row["username"],
                "display_name": (
                    row["display_name"]
                    or row["username"]
                )
            }
            for row in rows
        ])

    # ========================================================
    # BEKLEYEN İSTEKLER API
    # ========================================================

    @app.route("/api/friend-requests")
    @login_required
    def friend_requests_api():

        rows = get_pending_friend_requests(
            session["user_id"]
        )

        return jsonify([
            dict(row)
            for row in rows
        ])

    # ========================================================
    # KULLANICININ ODALARI API
    # ========================================================

    @app.route("/api/friend-rooms")
    @login_required
    def friend_rooms_api():

        rooms = get_user_friend_rooms(
            session["user_id"]
        )

        return jsonify([
            dict(room)
            for room in rooms
        ])

    # ========================================================
    # ARKADAŞ ODASI OLUŞTUR
    # ========================================================

    @app.route(
        "/friends/room/create",
        methods=["POST"]
    )
    @login_required
    def create_room():

        data = request.get_json(
            silent=True
        ) or request.form

        room_name = (
            data.get("name")
            or data.get("room_name")
            or "Arkadaş Sohbeti"
        ).strip()

        if len(room_name) > 50:
            room_name = room_name[:50]

        room_code = create_friend_room(
            room_name=room_name,
            owner_id=session["user_id"]
        )

        if not room_code:

            return jsonify({
                "success": False,
                "error": "Oda oluşturulamadı."
            }), 500

        return jsonify({
            "success": True,
            "room_code": room_code,
            "url": url_for(
                "friend_room",
                room_code=room_code
            )
        })

    # ========================================================
    # ARKADAŞ ODASINA KATIL
    # ========================================================

    @app.route(
        "/friends/room/join",
        methods=["POST"]
    )
    @login_required
    def join_room():

        data = request.get_json(
            silent=True
        ) or request.form

        room_code = (
            data.get("room_code")
            or data.get("code")
            or ""
        ).strip().upper()

        if not room_code:

            return jsonify({
                "success": False,
                "error": "Oda kodu gerekli."
            }), 400

        room = get_friend_room(
            room_code
        )

        if not room:

            return jsonify({
                "success": False,
                "error": "Oda bulunamadı."
            }), 404

        success = join_friend_room(
            room_code,
            session["user_id"]
        )

        if not success:

            return jsonify({
                "success": False,
                "error": "Odaya katılınamadı."
            }), 400

        return jsonify({
            "success": True,
            "room_code": room_code,
            "url": url_for(
                "friend_room",
                room_code=room_code
            )
        })

    # ========================================================
    # ARKADAŞ ODASI
    # ========================================================

    @app.route(
        "/friends/room/<room_code>"
    )
    @login_required
    def friend_room(room_code):

        room_code = (
            room_code
            or ""
        ).strip().upper()

        room = get_friend_room(
            room_code
        )

        if not room:

            return (
                "Arkadaş odası bulunamadı.",
                404
            )

        user_id = session["user_id"]

        # ====================================================
        # GÜVENLİK
        # ====================================================

        if not is_room_member(
            room_code,
            user_id
        ):

            return (
                "Bu odanın üyesi değilsiniz.",
                403
            )

        messages = get_friend_messages(
            room_code
        )

        members = get_friend_room_members(
            room_code
        )

        return render_template(
            "friend_room.html",
            room=room,
            room_code=room_code,
            messages=messages,
            members=members,
            user=current_user()
        )

    # ========================================================
    # ODA ÜYELERİ API
    # ========================================================

    @app.route(
        "/friends/room/<room_code>/members"
    )
    @login_required
    def room_members(room_code):

        room_code = (
            room_code
            or ""
        ).strip().upper()

        if not is_room_member(
            room_code,
            session["user_id"]
        ):

            return jsonify({
                "success": False,
                "error": "Bu odanın üyesi değilsiniz."
            }), 403

        members = get_friend_room_members(
            room_code
        )

        return jsonify([
            {
                "id": member["id"],
                "username": member["username"],
                "display_name": (
                    member["display_name"]
                    or member["username"]
                ),
                "joined_at": member["joined_at"]
            }
            for member in members
        ])

    # ========================================================
    # ARKADAŞ ODASI MESAJLARI
    # ========================================================

    @app.route(
        "/friends/room/<room_code>/messages",
        methods=["GET", "POST"]
    )
    @login_required
    def room_messages(room_code):

        room_code = (
            room_code
            or ""
        ).strip().upper()

        if not is_room_member(
            room_code,
            session["user_id"]
        ):

            return jsonify({
                "success": False,
                "error": "Bu odanın üyesi değilsiniz."
            }), 403

        # ====================================================
        # GET
        # ====================================================

        if request.method == "GET":

            limit = safe_int(
                request.args.get(
                    "limit",
                    200
                ),
                200
            )

            if limit <= 0:
                limit = 200

            if limit > 500:
                limit = 500

            rows = get_friend_messages(
                room_code,
                limit
            )

            return jsonify([
                dict(row)
                for row in rows
            ])

        # ====================================================
        # POST
        # ====================================================

        data = request.get_json(
            silent=True
        ) or request.form

        message = (
            data.get("message")
            or data.get("text")
            or ""
        ).strip()

        user = current_user()

        username = (
            user["display_name"]
            or user["username"]
        )

        if not message:

            return jsonify({
                "success": False,
                "error": "Mesaj boş olamaz."
            }), 400

        success = save_friend_message(
            room_code=room_code,
            username=username,
            message=message,
            user_id=session["user_id"]
        )

        if not success:

            return jsonify({
                "success": False,
                "error": "Mesaj kaydedilemedi."
            }), 500

        return jsonify({
            "success": True
        })

    # ========================================================
    # ARKADAŞ ODASINA FOTOĞRAF
    # ========================================================

    @app.route(
        "/friends/room/<room_code>/photo",
        methods=["POST"]
    )
    @login_required
    def room_photo(room_code):

        room_code = (
            room_code
            or ""
        ).strip().upper()

        if not is_room_member(
            room_code,
            session["user_id"]
        ):

            return jsonify({
                "success": False,
                "error": "Bu odanın üyesi değilsiniz."
            }), 403

        photo = request.files.get(
            "photo"
        )

        if not photo:

            return jsonify({
                "success": False,
                "error": "Fotoğraf seçilmedi."
            }), 400

        filename = photo.filename or ""

        if not filename:

            return jsonify({
                "success": False,
                "error": "Geçersiz dosya."
            }), 400

        extension = os.path.splitext(
            filename
        )[1].lower()

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp"
        }

        if extension not in allowed_extensions:

            return jsonify({
                "success": False,
                "error": "Bu dosya türüne izin verilmiyor."
            }), 400

        upload_folder = os.path.join(
            app.root_path,
            "uploads",
            "friends"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        new_filename = (
            uuid.uuid4().hex
            + extension
        )

        file_path = os.path.join(
            upload_folder,
            new_filename
        )

        photo.save(
            file_path
        )

        relative_path = os.path.join(
            "friends",
            new_filename
        ).replace(
            "\\",
            "/"
        )

        user = current_user()

        username = (
            user["display_name"]
            or user["username"]
        )

        success = save_friend_photo_message(
            room_code=room_code,
            username=username,
            photo_path=relative_path,
            user_id=session["user_id"]
        )

        if not success:

            try:
                os.remove(file_path)
            except OSError:
                pass

            return jsonify({
                "success": False,
                "error": "Fotoğraf mesajı kaydedilemedi."
            }), 500

        return jsonify({
            "success": True,
            "photo_path": relative_path
        })

    # ========================================================
    # ARKADAŞ FOTOĞRAFLARI
    # ========================================================

    @app.route(
        "/uploads/friends/<filename>"
    )
    @login_required
    def friend_upload(filename):

        return send_from_directory(
            os.path.join(
                app.root_path,
                "uploads",
                "friends"
            ),
            filename
        )

    # ========================================================
    # ARKADAŞ ODASI SİL
    # ========================================================

    @app.route(
        "/friends/room/<room_code>/delete",
        methods=["POST", "DELETE"]
    )
    @login_required
    def remove_friend_room(room_code):

        room_code = (
            room_code
            or ""
        ).strip().upper()

        success = delete_friend_room(
            room_code,
            session["user_id"]
        )

        if not success:

            return jsonify({
                "success": False,
                "error": "Oda silinemedi."
            }), 403

        return jsonify({
            "success": True
        })

    # ========================================================
    # PUSH BİLDİRİM ABONELİĞİ
    # ========================================================

    @app.route(
        "/api/push/subscribe",
        methods=["POST"]
    )
    @login_required
    def push_subscribe():

        data = request.get_json(
            silent=True
        ) or {}

        endpoint = (
            data.get("endpoint")
            or ""
        ).strip()

        keys = data.get(
            "keys"
        ) or {}

        p256dh = (
            keys.get("p256dh")
            or data.get("p256dh")
            or ""
        ).strip()

        auth = (
            keys.get("auth")
            or data.get("auth")
            or ""
        ).strip()

        success = save_push_subscription(
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            user_id=session["user_id"]
        )

        if not success:

            return jsonify({
                "success": False,
                "error": "Push aboneliği kaydedilemedi."
            }), 400

        return jsonify({
            "success": True
        })

    # ========================================================
    # PUSH ABONELİĞİ SİL
    # ========================================================

    @app.route(
        "/api/push/unsubscribe",
        methods=["POST"]
    )
    @login_required
    def push_unsubscribe():

        data = request.get_json(
            silent=True
        ) or {}

        endpoint = (
            data.get("endpoint")
            or ""
        ).strip()

        success = delete_push_subscription(
            endpoint
        )

        return jsonify({
            "success": success
        })

    # ========================================================
    # PUSH ABONELİKLERİ
    # ========================================================

    @app.route(
        "/api/push/subscriptions"
    )
    @login_required
    def push_subscriptions():

        rows = get_push_subscriptions(
            session["user_id"]
        )

        return jsonify([
            dict(row)
            for row in rows
        ])

    # ========================================================
    # API: OTURUM BİLGİSİ
    # ========================================================

    @app.route(
        "/api/me"
    )
    @login_required
    def api_me():

        user = current_user()

        if not user:

            session.clear()

            return jsonify({
                "success": False,
                "error": "Oturum bulunamadı."
            }), 401

        return jsonify({
            "success": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "display_name": (
                    user["display_name"]
                    or user["username"]
                ),
                "created_at": user["created_at"]
            }
        })

    # ========================================================
    # TEST ROUTE
    # ========================================================

    @app.route("/test")
    def test():

        return jsonify({
            "success": True,
            "message": "MaviGPT çalışıyor.",
            "database": "connected"
        })

    # ========================================================
    # 404
    # ========================================================

    @app.errorhandler(404)
    def page_not_found(error):

        if request.path.startswith("/api/"):

            return jsonify({
                "success": False,
                "error": "İstek bulunamadı."
            }), 404

        return (
            "Sayfa bulunamadı.",
            404
        )

    # ========================================================
    # 500
    # ========================================================

    @app.errorhandler(500)
    def internal_server_error(error):

        print(
            "500 HATASI:",
            repr(error)
        )

        if request.path.startswith("/api/"):

            return jsonify({
                "success": False,
                "error": "Sunucu hatası oluştu."
            }), 500

        return (
            "Sunucuda bir hata oluştu.",
            500
        )
