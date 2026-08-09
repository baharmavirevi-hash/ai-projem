import sqlite3

DB_NAME = "chat.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # ==============================
    # MAVIGPT SOHBETLERİ
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_type TEXT NOT NULL,
            user_message TEXT,
            ai_message TEXT
        )
    """)

    # ==============================
    # SAĞLIK KAYITLARI
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptom TEXT,
            medicine TEXT,
            note TEXT
        )
    """)

    # ==============================
    # REGL
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS period_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT,
            end_date TEXT,
            note TEXT
        )
    """)

    # ==============================
    # SİNDİRİM
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diarrhea_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            count INTEGER,
            condition TEXT,
            note TEXT
        )
    """)

    # ==============================
    # İLAÇLAR
    # ==============================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dose TEXT,
            hour TEXT,
            start_date TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# MAVIGPT
# ============================================================

def save_chat(chat_type, user_message, ai_message):

    conn = get_db()

    conn.execute("""
        INSERT INTO messages
        (
            chat_type,
            user_message,
            ai_message
        )
        VALUES (?, ?, ?)
    """, (
        chat_type,
        user_message,
        ai_message
    ))

    conn.commit()
    conn.close()


def get_chats(chat_type="normal"):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            chat_type,
            user_message,
            ai_message
        FROM messages
        WHERE chat_type = ?
        ORDER BY id DESC
    """, (
        chat_type,
    )).fetchall()

    conn.close()

    return rows


def get_chat(chat_id):

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            chat_type,
            user_message,
            ai_message
        FROM messages
        WHERE id = ?
    """, (
        chat_id,
    )).fetchone()

    conn.close()

    return row


# ============================================================
# SAĞLIK
# ============================================================

def save_health_record(symptom, medicine, note):

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

def save_period_record(start_date, end_date, note):

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

def save_diarrhea_record(date, count, condition, note):

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
# İLAÇLAR
# ============================================================

def save_medicine(name, dose, hour, start_date):

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
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


def delete_medicine(medicine_id):

    conn = get_db()

    conn.execute("""
        DELETE FROM medicines
        WHERE id = ?
    """, (
        medicine_id,
    ))

    conn.commit()
    conn.close()
