import sqlite3
import os


# ============================================================
# DATABASE AYARLARI
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "chat.db")


# ============================================================
# DATABASE BAĞLANTISI
# ============================================================

def get_db():

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# DATABASE OLUŞTUR
# ============================================================

def init_db():

    conn = get_db()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # SOHBETLER
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            chat_type TEXT DEFAULT 'normal',

            message TEXT,

            response TEXT,

            title TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # --------------------------------------------------------
    # ESKİ VERİTABANLARINA TITLE EKLE
    # --------------------------------------------------------

    columns = cursor.execute("""
        PRAGMA table_info(chats)
    """).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    if "title" not in column_names:

        cursor.execute("""
            ALTER TABLE chats
            ADD COLUMN title TEXT
        """)

        cursor.execute("""
            UPDATE chats
            SET title = message
            WHERE title IS NULL
               OR title = ''
        """)

    # --------------------------------------------------------
    # SAĞLIK
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # REGL
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SİNDİRİM
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # İLAÇLAR
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # AYARLAR
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            id INTEGER PRIMARY KEY CHECK (id = 1),

            mode TEXT DEFAULT 'normal',

            personality TEXT DEFAULT 'friendly'

        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO settings
        (id, mode, personality)

        VALUES
        (1, 'normal', 'friendly')
    """)

    conn.commit()
    conn.close()


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
            response,
            title
        )

        VALUES (?, ?, ?, ?)
    """, (
        chat_type,
        message,
        response,
        message[:60]
    ))

    conn.commit()
    conn.close()


# ============================================================
# SOHBET BAŞLIĞINI DÜZENLE
# ============================================================

def update_chat_title(
    chat_id,
    title
):

    title = (title or "").strip()

    if not title:
        return False

    title = title[:100]

    conn = get_db()

    cursor = conn.execute("""
        UPDATE chats

        SET title = ?

        WHERE id = ?
    """, (
        title,
        chat_id
    ))

    conn.commit()

    changed = cursor.rowcount > 0

    conn.close()

    return changed


# ============================================================
# SOHBET SİL
# ============================================================

def delete_chat(
    chat_id
):

    conn = get_db()

    cursor = conn.execute("""
        DELETE FROM chats

        WHERE id = ?
    """, (
        chat_id,
    ))

    conn.commit()

    deleted = cursor.rowcount > 0

    conn.close()

    return deleted


# ============================================================
# TÜM SOHBET MESAJLARINI GETİR
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
            title,
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
            title,
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
            title,
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

    return get_chat(chat_id)


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
# BAŞLAT
# ============================================================

init_db()
