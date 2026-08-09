import sqlite3
import os
from datetime import datetime


# ============================================================
# VERİTABANI AYARI
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(
    BASE_DIR,
    "chat.db"
)


# ============================================================
# VERİTABANI BAĞLANTISI
# ============================================================

def get_db():

    conn = sqlite3.connect(
        DB_NAME,
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# VERİTABANINI OLUŞTUR
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

            created_at TEXT

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

            created_at TEXT

        )
    """)


    # --------------------------------------------------------
    # REGL TAKİBİ
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS period_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            start_date TEXT,

            end_date TEXT,

            note TEXT,

            created_at TEXT

        )
    """)


    # --------------------------------------------------------
    # SİNDİRİM TAKİBİ
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diarrhea_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT,

            count INTEGER DEFAULT 0,

            condition TEXT,

            note TEXT,

            created_at TEXT

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

            hour TEXT NOT NULL,

            start_date TEXT,

            created_at TEXT

        )
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

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chats (
            chat_type,
            message,
            response,
            created_at
        )

        VALUES (?, ?, ?, ?)
    """, (
        chat_type,
        message,
        response,
        datetime.now().isoformat()
    ))

    conn.commit()

    conn.close()


# ============================================================
# SOHBETLERİ GETİR
# ============================================================

def get_chats(
    chat_type="normal"
):

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
# SAĞLIK KAYDI EKLE
# ============================================================

def save_health_record(
    symptom,
    medicine,
    note
):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO health_records (
            symptom,
            medicine,
            note,
            created_at
        )

        VALUES (?, ?, ?, ?)
    """, (
        symptom,
        medicine,
        note,
        datetime.now().isoformat()
    ))

    conn.commit()

    conn.close()


# ============================================================
# SAĞLIK KAYITLARINI GETİR
# ============================================================

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
# REGL KAYDI EKLE
# ============================================================

def save_period_record(
    start_date,
    end_date,
    note
):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO period_records (
            start_date,
            end_date,
            note,
            created_at
        )

        VALUES (?, ?, ?, ?)
    """, (
        start_date,
        end_date,
        note,
        datetime.now().isoformat()
    ))

    conn.commit()

    conn.close()


# ============================================================
# REGL KAYITLARINI GETİR
# ============================================================

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


# ============================================================
# SİNDİRİM KAYDI EKLE
# ============================================================

def save_diarrhea_record(
    date,
    count,
    condition,
    note
):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diarrhea_records (
            date,
            count,
            condition,
            note,
            created_at
        )

        VALUES (?, ?, ?, ?, ?)
    """, (
        date,
        count,
        condition,
        note,
        datetime.now().isoformat()
    ))

    conn.commit()

    conn.close()


# ============================================================
# SİNDİRİM KAYITLARINI GETİR
# ============================================================

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

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO medicines (
            name,
            dose,
            hour,
            start_date,
            created_at
        )

        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        dose,
        hour,
        start_date,
        datetime.now().isoformat()
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
            hour ASC,
            id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ============================================================
# İLAÇ SİL
# ============================================================

def delete_medicine(
    medicine_id
):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM medicines
        WHERE id = ?
    """, (
        medicine_id,
    ))

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    return deleted


# ============================================================
# BAŞLANGIÇTA VERİTABANINI HAZIRLA
# ============================================================

init_db()
