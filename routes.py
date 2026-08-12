import sqlite3
import os


# ============================================================
# DATABASE AYARLARI
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_NAME = os.path.join(
    BASE_DIR,
    "chat.db"
)


# ============================================================
# DATABASE BAĞLANTISI
# ============================================================

def get_db():

    conn = sqlite3.connect(
        DB_NAME
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# DATABASE OLUŞTUR
# ============================================================

def init_db():

    conn = get_db()

    cursor = conn.cursor()


    # ========================================================
    # MAVİGPT SOHBETLERİ
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            chat_type TEXT DEFAULT 'normal',

            message TEXT,

            response TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # SAĞLIK
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symptom TEXT,

            medicine TEXT,

            note TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # REGL
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS period_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            start_date TEXT,

            end_date TEXT,

            note TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # SİNDİRİM
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diarrhea_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT,

            count INTEGER DEFAULT 0,

            condition TEXT,

            note TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # İLAÇLAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            dose TEXT,

            hour TEXT,

            start_date TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # AYARLAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            id INTEGER PRIMARY KEY CHECK (id = 1),

            mode TEXT DEFAULT 'normal',

            personality TEXT DEFAULT 'friendly'

        )
    """)


    cursor.execute("""
        INSERT OR IGNORE INTO settings
        (
            id,
            mode,
            personality
        )

        VALUES
        (
            1,
            'normal',
            'friendly'
        )
    """)


    conn.commit()

    conn.close()
    # ============================================================
# 2. BÖLÜM — MAVİGPT SOHBET İŞLEMLERİ
# ============================================================


# ============================================================
# SOHBET KAYDET
# ============================================================

def save_chat(
    chat_type,
    message,
    response
):

    conn = get_db()

    conn.execute("""
        INSERT INTO chats
        (
            chat_type,
            message,
            response
        )

        VALUES (?, ?, ?)
    """, (
        chat_type,
        message,
        response
    ))

    conn.commit()

    conn.close()


# ============================================================
# TÜM MAVİGPT MESAJLARINI GETİR
# ============================================================

def get_chat_messages(
    chat_type="normal"
):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            chat_type,
            message,
            response,
            created_at

        FROM chats

        WHERE chat_type = ?

        ORDER BY id ASC
    """, (
        chat_type,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# SON SOHBETLER
# ============================================================

def get_chats(
    chat_type="normal"
):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            chat_type,
            message,
            response,
            created_at

        FROM chats

        WHERE chat_type = ?

        ORDER BY id DESC
    """, (
        chat_type,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# TEK SOHBET
# ============================================================

def get_chat(
    chat_id
):

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            chat_type,
            message,
            response,
            created_at

        FROM chats

        WHERE id = ?

        LIMIT 1
    """, (
        chat_id,
    )).fetchone()

    conn.close()

    return row


# ============================================================
# ID İLE SOHBET
# ============================================================

def get_chat_by_id(
    chat_id
):

    return get_chat(
        chat_id
    )


# ============================================================
# SOHBET BAŞLIĞINI / MESAJINI DÜZENLE
# ============================================================

def update_chat_title(
    chat_id,
    title
):

    conn = get_db()

    conn.execute("""
        UPDATE chats

        SET message = ?

        WHERE id = ?
    """, (
        title,
        chat_id
    ))

    conn.commit()

    conn.close()


# ============================================================
# SOHBET SİL
# ============================================================

def delete_chat(
    chat_id
):

    conn = get_db()

    conn.execute("""
        DELETE FROM chats

        WHERE id = ?
    """, (
        chat_id,
    ))

    conn.commit()

    conn.close()
    # ============================================================
# 3. BÖLÜM — SAĞLIK KAYITLARI
# ============================================================


# ============================================================
# SAĞLIK KAYDI KAYDET
# ============================================================

def save_health_record(
    symptom,
    medicine,
    note
):

    conn = get_db()

    conn.execute("""
        INSERT INTO health_records
        (
            symptom,
            medicine,
            note
        )

        VALUES (?, ?, ?)
    """, (
        symptom,
        medicine,
        note
    ))

    conn.commit()

    conn.close()


# ============================================================
# SAĞLIK KAYITLARINI GETİR
# ============================================================

def get_health_records():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            symptom,
            medicine,
            note,
            created_at

        FROM health_records

        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows
    # ============================================================
# 4. BÖLÜM — REGL KAYITLARI
# ============================================================


# ============================================================
# REGL KAYDI KAYDET
# ============================================================

def save_period_record(
    start_date,
    end_date,
    note
):

    conn = get_db()

    conn.execute("""
        INSERT INTO period_records
        (
            start_date,
            end_date,
            note
        )

        VALUES (?, ?, ?)
    """, (
        start_date,
        end_date,
        note
    ))

    conn.commit()

    conn.close()


# ============================================================
# REGL KAYITLARINI GETİR
# ============================================================

def get_period_records():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            start_date,
            end_date,
            note,
            created_at

        FROM period_records

        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows
    # ============================================================
# 5. BÖLÜM — SİNDİRİM KAYITLARI
# ============================================================


# ============================================================
# SİNDİRİM KAYDI KAYDET
# ============================================================

def save_diarrhea_record(
    date,
    count,
    condition,
    note
):

    conn = get_db()

    conn.execute("""
        INSERT INTO diarrhea_records
        (
            date,
            count,
            condition,
            note
        )

        VALUES (?, ?, ?, ?)
    """, (
        date,
        count,
        condition,
        note
    ))

    conn.commit()

    conn.close()


# ============================================================
# SİNDİRİM KAYITLARINI GETİR
# ============================================================

def get_diarrhea_records():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            date,
            count,
            condition,
            note,
            created_at

        FROM diarrhea_records

        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows
    # ============================================================
# 6. BÖLÜM — İLAÇ SİSTEMİ
# ============================================================


# ============================================================
# İLAÇ KAYDET
# ============================================================

def save_medicine(
    name,
    dose,
    hour,
    start_date
):

    conn = get_db()

    conn.execute("""
        INSERT INTO medicines
        (
            name,
            dose,
            hour,
            start_date
        )

        VALUES (?, ?, ?, ?)
    """, (
        name,
        dose,
        hour,
        start_date
    ))

    conn.commit()

    conn.close()


# ============================================================
# İLAÇLARI GETİR
# ============================================================

def get_medicines():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            name,
            dose,
            hour,
            start_date,
            created_at

        FROM medicines

        ORDER BY

            CASE

                WHEN hour IS NULL
                     OR hour = ''

                THEN 1

                ELSE 0

            END,

            hour ASC,

            id DESC

    """).fetchall()

    conn.close()

    return rows


# ============================================================
# İLAÇ SİL
# ============================================================

def delete_medicine(
    medicine_id
):

    conn = get_db()

    conn.execute("""
        DELETE FROM medicines

        WHERE id = ?
    """, (
        medicine_id,
    ))

    conn.commit()

    conn.close()
    # ============================================================
# 7. BÖLÜM — AYARLAR SİSTEMİ
# ============================================================


# ============================================================
# AYARLARI GETİR
# ============================================================

def get_settings():

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            mode,
            personality

        FROM settings

        WHERE id = 1

        LIMIT 1
    """).fetchone()

    conn.close()

    if row:

        return row

    return {
        "mode": "normal",
        "personality": "friendly"
    }


# ============================================================
# AYARLARI KAYDET
# ============================================================

def save_settings(
    mode,
    personality
):

    allowed_modes = {
        "normal",
        "creative",
        "study",
        "concise"
    }

    allowed_personalities = {
        "friendly",
        "funny",
        "serious",
        "teacher"
    }

    # --------------------------------------------------------
    # GEÇERSİZ MODU ENGELLE
    # --------------------------------------------------------

    if mode not in allowed_modes:

        mode = "normal"

    # --------------------------------------------------------
    # GEÇERSİZ KİŞİLİĞİ ENGELLE
    # --------------------------------------------------------

    if personality not in allowed_personalities:

        personality = "friendly"

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    conn = get_db()

    conn.execute("""
        UPDATE settings

        SET
            mode = ?,
            personality = ?

        WHERE id = 1
    """, (
        mode,
        personality
    ))

    conn.commit()

    conn.close()
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
# ARKADAŞ SOHBETİ ANA SAYFA
# ========================================================

@app.route(
    "/friends",
    methods=["GET", "POST"]
)
def friends():

    error = None
    room = None
    room_code = ""

    # ----------------------------------------------------
    # POST
    # ----------------------------------------------------

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        ).strip()

        # =================================================
        # YENİ ODA OLUŞTUR
        # =================================================

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
                    "ARKADAŞ ODASI OLUŞTURMA HATASI:",
                    repr(e)
                )

                error = (
                    "Sohbet odası oluşturulamadı."
                )

        # =================================================
        # ODAYA KATIL
        # =================================================

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
                            "Bu sohbet koduna ait oda bulunamadı."
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
                        "Sohbet odası bulunurken bir hata oluştu."
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

    room = get_friend_room(
        room_code
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
                    "ARKADAŞ MESAJI KAYIT HATASI:",
                    repr(e)
                )

                error = (
                    "Mesaj gönderilirken bir hata oluştu."
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
