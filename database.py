import sqlite3
import os
import secrets


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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    # ARKADAŞ SOHBET ODALARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT UNIQUE NOT NULL,
            room_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ========================================================
    # ARKADAŞ MESAJLARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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
# MESAJLARI GETİR
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
# SOHBETLERİ GETİR
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
# SOHBET BAŞLIĞI / MESAJ DÜZENLE
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
# SAĞLIK KAYDI
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
# SAĞLIK KAYITLARI
# ============================================================

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
# REGL KAYDI
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
# REGL KAYITLARI
# ============================================================

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
# SİNDİRİM KAYDI
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
# SİNDİRİM KAYITLARI
# ============================================================

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
# İLAÇ KAYDI
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
        SELECT *
        FROM medicines
        ORDER BY id DESC
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
# AYARLARI GETİR
# ============================================================

def get_settings():

    conn = get_db()

    row = conn.execute("""
        SELECT
            mode,
            personality
        FROM settings
        WHERE id = 1
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

    conn = get_db()

    conn.execute("""
        INSERT OR REPLACE INTO settings
        (
            id,
            mode,
            personality
        )
        VALUES (1, ?, ?)
    """, (
        mode,
        personality
    ))

    conn.commit()
    conn.close()


# ============================================================
# ARKADAŞ SOHBET ODASI OLUŞTUR
# ============================================================

def create_friend_room(
    room_name
):

    conn = get_db()

    while True:

        room_code = secrets.token_hex(3).upper()

        existing = conn.execute("""
            SELECT id
            FROM friend_rooms
            WHERE room_code = ?
        """, (
            room_code,
        )).fetchone()

        if not existing:
            break

    conn.execute("""
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
# ARKADAŞ ODASI GETİR
# ============================================================

def get_friend_room(
    room_code
):

    conn = get_db()

    row = conn.execute("""
        SELECT *
        FROM friend_rooms
        WHERE room_code = ?
        LIMIT 1
    """, (
        room_code,
    )).fetchone()

    conn.close()

    return row


# ============================================================
# ARKADAŞ MESAJI KAYDET
# ============================================================

def save_friend_message(
    room_code,
    username,
    message
):

    conn = get_db()

    conn.execute("""
        INSERT INTO friend_messages
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

    conn.commit()
    conn.close()

    return True


# ============================================================
# ARKADAŞ MESAJLARINI GETİR
# ============================================================

def get_friend_messages(
    room_code
):

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM friend_messages
        WHERE room_code = ?
        ORDER BY id ASC
    """, (
        room_code,
    )).fetchall()

    conn.close()

    return rows
