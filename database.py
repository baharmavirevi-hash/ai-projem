import sqlite3
import os
from datetime import datetime


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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # SAĞLIK KAYITLARI
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptom TEXT,
            medicine TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # REGL KAYITLARI
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS period_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT,
            end_date TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # SİNDİRİM KAYITLARI
    # --------------------------------------------------------

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# MAVIGPT SOHBETLERİ
# ============================================================

def save_chat(chat_type, message, response):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
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


def get_chats(chat_type="normal"):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM chats
        WHERE chat_type = ?
        ORDER BY id DESC
    """, (
        chat_type,
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


# ============================================================
# SAĞLIK KAYITLARI
# ============================================================

def save_health_record(
    symptom="",
    medicine="",
    note=""
):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
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

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM health_records
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ============================================================
# REGL KAYITLARI
# ============================================================

def save_period_record(
    start_date,
    end_date="",
    note=""
):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
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

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM period_records
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_period_record(record_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM period_records
        WHERE id = ?
    """, (
        record_id,
    ))

    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


# ============================================================
# SİNDİRİM KAYITLARI
# ============================================================

def save_diarrhea_record(
    date,
    count=0,
    condition="",
    note=""
):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
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

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM diarrhea_records
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_diarrhea_record(record_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM diarrhea_records
        WHERE id = ?
    """, (
        record_id,
    ))

    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


# ============================================================
# İLAÇ KAYDET
# ============================================================

def save_medicine(
    name,
    dose="",
    hour="",
    start_date=""
):

    name = str(name or "").strip()
    dose = str(dose or "").strip()
    hour = str(hour or "").strip()
    start_date = str(start_date or "").strip()

    if not name:
        return False

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
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

    medicine_id = cursor.lastrowid

    conn.close()

    return medicine_id


# ============================================================
# İLAÇLARI GETİR
# ============================================================

def get_medicines():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
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
                WHEN hour IS NULL OR hour = ''
                THEN 1
                ELSE 0
            END,
            hour ASC,
            id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ============================================================
# TEK İLAÇ GETİR
# ============================================================

def get_medicine(medicine_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM medicines
        WHERE id = ?
    """, (
        medicine_id,
    ))

    row = cursor.fetchone()

    conn.close()

    return row


# ============================================================
# İLAÇ SİL
# ============================================================

def delete_medicine(medicine_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM medicines
        WHERE id = ?
    """, (
        medicine_id,
    ))

    deleted = cursor.rowcount > 0

    conn.commit()

    conn.close()

    return deleted


# ============================================================
# TÜM İLAÇLARI SİL
# ============================================================

def delete_all_medicines():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM medicines
    """)

    deleted_count = cursor.rowcount

    conn.commit()

    conn.close()

    return deleted_count


# ============================================================
# DATABASE BAŞLAT
# ============================================================

init_db()
