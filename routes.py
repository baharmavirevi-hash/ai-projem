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
