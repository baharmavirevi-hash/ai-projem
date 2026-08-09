import sqlite3
import os
from contextlib import contextmanager


# ============================================================
# DATABASE AYARLARI
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "chat.db")


# ============================================================
# DATABASE BAĞLANTISI
# ============================================================

def get_db():
    """
    SQLite veritabanına güvenli bağlantı açar.
    """
    conn = sqlite3.connect(
        DB_NAME,
        timeout=10
    )

    conn.row_factory = sqlite3.Row

    # SQLite'ın foreign key desteğini aktif eder
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


@contextmanager
def db_connection():
    """
    Database bağlantısını güvenli şekilde yönetir.
    """
    conn = get_db()

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# DATABASE OLUŞTURMA
# ============================================================

def init_db():

    with db_connection() as conn:

        cursor = conn.cursor()

        # ----------------------------------------------------
        # SOHBETLER
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                message TEXT,
                reply TEXT,
                chat_type TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # SAĞLIK KAYITLARI
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symptom TEXT,
                medicine TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # REGL KAYITLARI
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS period_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT,
                end_date TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # SİNDİRİM KAYITLARI
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # İLAÇLAR
        # ----------------------------------------------------

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


# ============================================================
# SOHBET
# ============================================================

def save_chat(chat_type, message, reply):

    with db_connection() as conn:

        conn.execute("""
            INSERT INTO messages
            (
                chat_type,
                message,
                reply
            )
            VALUES (?, ?, ?)
        """, (
            chat_type,
            message,
            reply
        ))


def get_chats(chat_type="normal"):

    with db_connection() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM messages
            WHERE chat_type = ?
            ORDER BY id DESC
        """, (
            chat_type,
        ))

        return cursor.fetchall()


def delete_chat(chat_id):

    with db_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM messages
            WHERE id = ?
        """, (
            chat_id,
        ))

        return cursor.rowcount > 0


# ============================================================
# SAĞLIK
# ============================================================

def save_health_record(
    symptom,
    medicine,
    note
):

    with db_connection() as conn:

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


def get_health_records():

    with db_connection() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM health_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def delete_health_record(record_id):

    with db_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM health_records
            WHERE id = ?
        """, (
            record_id,
        ))

        return cursor.rowcount > 0


# ============================================================
# REGL
# ============================================================

def save_period_record(
    start_date,
    end_date,
    note
):

    with db_connection() as conn:

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


def get_period_records():

    with db_connection() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM period_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def delete_period_record(record_id):

    with db_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM period_records
            WHERE id = ?
        """, (
            record_id,
        ))

        return cursor.rowcount > 0


# ============================================================
# SİNDİRİM
# ============================================================

def save_diarrhea_record(
    date,
    count,
    condition,
    note
):

    try:
        count = int(count)

    except (ValueError, TypeError):
        count = 0

    if count < 0:
        count = 0

    with db_connection() as conn:

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


def get_diarrhea_records():

    with db_connection() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM diarrhea_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def delete_diarrhea_record(record_id):

    with db_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM diarrhea_records
            WHERE id = ?
        """, (
            record_id,
        ))

        return cursor.rowcount > 0


# ============================================================
# İLAÇLAR
# ============================================================

def save_medicine(
    name,
    dose,
    hour,
    start_date
):

    name = (name or "").strip()
    dose = (dose or "").strip()
    hour = (hour or "").strip()
    start_date = (start_date or "").strip()

    if not name:
        raise ValueError("İlaç adı boş bırakılamaz.")

    with db_connection() as conn:

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


def get_medicines():

    with db_connection() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM medicines
            ORDER BY
                CASE
                    WHEN hour IS NULL OR hour = '' THEN 1
                    ELSE 0
                END,
                hour ASC,
                id DESC
        """)

        return cursor.fetchall()


def delete_medicine(medicine_id):

    try:
        medicine_id = int(medicine_id)

    except (ValueError, TypeError):
        return False

    with db_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM medicines
            WHERE id = ?
        """, (
            medicine_id,
        ))

        return cursor.rowcount > 0


# ============================================================
# TEK İLAÇ GETİR
# ============================================================

def get_medicine(medicine_id):

    try:
        medicine_id = int(medicine_id)

    except (ValueError, TypeError):
        return None

    with db_connection() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM medicines
            WHERE id = ?
        """, (
            medicine_id,
        ))

        return cursor.fetchone()


# ============================================================
# DATABASE BAŞLAT
# ============================================================

try:

    init_db()

    print("================================")
    print("DATABASE HAZIR")
    print("DB:", DB_NAME)
    print("================================")

except Exception as e:

    print("================================")
    print("DATABASE BASLATMA HATASI")
    print(repr(e))
    print("================================")
