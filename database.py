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


    # ========================================================
    # ESKİ ARKADAŞ SİSTEMİ
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # ESKİ ARKADAŞ MESAJLARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            friend_id INTEGER NOT NULL,

            message TEXT NOT NULL,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (friend_id)
                REFERENCES friends(id)
                ON DELETE CASCADE

        )
    """)


    # ========================================================
    # 🆕 ARKADAŞ SOHBET ODALARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_rooms (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_code TEXT UNIQUE NOT NULL,

            room_name TEXT NOT NULL,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # 🆕 ARKADAŞ ODA MESAJLARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_room_messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_code TEXT NOT NULL,

            username TEXT NOT NULL,

            message TEXT NOT NULL,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # DEĞİŞİKLİKLERİ KAYDET
    # ========================================================

    conn.commit()

    conn.close()
    # ============================================================
# MAVİGPT SOHBET KAYDET
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
# SAĞLIK
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


def get_health_records():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM health_records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


# ============================================================
# REGL
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


def get_period_records():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM period_records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


# ============================================================
# SİNDİRİM
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


def get_diarrhea_records():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM diarrhea_records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows
    # ============================================================
# İLAÇ
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


def get_medicines():

    conn = get_db()

    rows = conn.execute("""
        SELECT *

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
# AYARLAR
# ============================================================

def get_settings():

    conn = get_db()

    row = conn.execute("""
        SELECT *

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

    if mode not in allowed_modes:

        mode = "normal"

    if personality not in allowed_personalities:

        personality = "friendly"

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
    # ============================================================
# ARKADAŞ EKLE
# ============================================================

def add_friend(
    name
):

    name = (
        name
        or ""
    ).strip()

    if not name:

        return None

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO friends
        (
            name
        )

        VALUES (?)
    """, (
        name,
    ))

    friend_id = cursor.lastrowid

    conn.commit()

    conn.close()

    return friend_id


# ============================================================
# TÜM ARKADAŞLARI GETİR
# ============================================================

def get_friends():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            name,
            created_at

        FROM friends

        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


# ============================================================
# TEK ARKADAŞ
# ============================================================

def get_friend(
    friend_id
):

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            name,
            created_at

        FROM friends

        WHERE id = ?

        LIMIT 1
    """, (
        friend_id,
    )).fetchone()

    conn.close()

    return row


# ============================================================
# ARKADAŞ SİL
# ============================================================

def delete_friend(
    friend_id
):

    conn = get_db()

    conn.execute("""
        DELETE FROM friend_messages

        WHERE friend_id = ?
    """, (
        friend_id,
    ))

    conn.execute("""
        DELETE FROM friends

        WHERE id = ?
    """, (
        friend_id,
    ))

    conn.commit()

    conn.close()


# ============================================================
# ESKİ ARKADAŞA MESAJ KAYDET
# ============================================================

def save_old_friend_message(
    friend_id,
    message
):

    message = (
        message
        or ""
    ).strip()

    if not message:

        return None

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO friend_messages
        (
            friend_id,
            message
        )

        VALUES (?, ?)
    """, (
        friend_id,
        message
    ))

    message_id = cursor.lastrowid

    conn.commit()

    conn.close()

    return message_id


# ============================================================
# ESKİ ARKADAŞ MESAJLARINI GETİR
# ============================================================

def get_old_friend_messages(
    friend_id
):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            friend_id,
            message,
            created_at

        FROM friend_messages

        WHERE friend_id = ?

        ORDER BY id ASC
    """, (
        friend_id,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# SON ESKİ ARKADAŞ MESAJLARI
# ============================================================

def get_recent_friend_messages(
    friend_id,
    limit=50
):

    try:

        limit = int(limit)

    except (
        ValueError,
        TypeError
    ):

        limit = 50

    if limit < 1:

        limit = 50

    if limit > 200:

        limit = 200

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            friend_id,
            message,
            created_at

        FROM friend_messages

        WHERE friend_id = ?

        ORDER BY id DESC

        LIMIT ?
    """, (
        friend_id,
        limit
    )).fetchall()

    conn.close()

    return list(
        reversed(rows)
    )
    # ============================================================
# ARKADAŞ SOHBET ODASI
# ============================================================

def create_friend_room(
    room_name="Arkadaş Sohbeti"
):

    room_name = (
        room_name
        or "Arkadaş Sohbeti"
    ).strip()

    if not room_name:

        room_name = "Arkadaş Sohbeti"


    # --------------------------------------------------------
    # BENZERSİZ ODA KODU OLUŞTUR
    # --------------------------------------------------------

    import uuid

    conn = get_db()

    while True:

        room_code = (
            uuid.uuid4()
            .hex[:8]
            .upper()
        )

        existing = conn.execute("""
            SELECT id

            FROM friend_rooms

            WHERE room_code = ?

            LIMIT 1
        """, (
            room_code,
        )).fetchone()

        if not existing:

            break


    # --------------------------------------------------------
    # ODAYI KAYDET
    # --------------------------------------------------------

    cursor = conn.execute("""
        INSERT INTO friend_rooms
        (
            room_code,
            room_name
        )

        VALUES (?, ?)
    """, (
        room_code,
        room_name
    ))

    conn.commit()

    conn.close()

    return room_code


# ============================================================
# ARKADAŞ ODASINI GETİR
# ============================================================

def get_friend_room(
    room_code
):

    room_code = (
        room_code
        or ""
    ).strip().upper()

    if not room_code:

        return None

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            room_code,
            room_name,
            created_at

        FROM friend_rooms

        WHERE room_code = ?

        LIMIT 1
    """, (
        room_code,
    )).fetchone()

    conn.close()

    return row


# ============================================================
# ARKADAŞ ODASINA MESAJ KAYDET
# ============================================================

def save_friend_message(
    room_code,
    username,
    message
):

    room_code = (
        room_code
        or ""
    ).strip().upper()

    username = (
        username
        or "Misafir"
    ).strip()

    message = (
        message
        or ""
    ).strip()


    if not room_code:

        return None

    if not message:

        return None

    if not username:

        username = "Misafir"


    conn = get_db()


    # --------------------------------------------------------
    # ODA VAR MI?
    # --------------------------------------------------------

    room = conn.execute("""
        SELECT id

        FROM friend_rooms

        WHERE room_code = ?

        LIMIT 1
    """, (
        room_code,
    )).fetchone()


    if not room:

        conn.close()

        return None


    # --------------------------------------------------------
    # MESAJI KAYDET
    # --------------------------------------------------------

    cursor = conn.execute("""
        INSERT INTO friend_room_messages
        (
            room_code,
            username,
            message
        )

        VALUES (?, ?, ?)
    """, (
        room_code,
        username,
        message
    ))


    message_id = cursor.lastrowid

    conn.commit()

    conn.close()

    return message_id


# ============================================================
# ARKADAŞ ODASI MESAJLARINI GETİR
# ============================================================

def get_friend_messages(
    room_code
):

    room_code = (
        room_code
        or ""
    ).strip().upper()

    if not room_code:

        return []


    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            room_code,
            username,
            message,
            created_at

        FROM friend_room_messages

        WHERE room_code = ?

        ORDER BY id ASC
    """, (
        room_code,
    )).fetchall()

    conn.close()

    return rows
   # ============================================================
# DATABASE BAŞLAT
# ============================================================

init_db() 
