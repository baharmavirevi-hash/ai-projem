import sqlite3
import os
from contextlib import contextmanager


# ============================================================
# VERİTABANI AYARLARI
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "chat.db")


# ============================================================
# VERİTABANI BAĞLANTISI
# ============================================================

def get_db():
    """
    SQLite veritabanına bağlantı oluşturur.
    """

    conn = sqlite3.connect(
        DB_NAME,
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    # SQLite'ın foreign key desteğini aktif et
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


@contextmanager
def db_connection():
    """
    Güvenli veritabanı bağlantısı.
    İşlem başarılıysa commit,
    hata olursa rollback yapar.
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
# VERİTABANINI OLUŞTUR
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
        # SİNDİRİM / İSHAL KAYITLARI
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diarrhea_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                count INTEGER,
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
                note TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # ESKİ VERİTABANINDA medicines TABLOSU VARSA
        # note SÜTUNUNU EKLE
        # ----------------------------------------------------

        cursor.execute("""
            PRAGMA table_info(medicines)
        """)

        columns = [
            row["name"]
            for row in cursor.fetchall()
        ]

        if "note" not in columns:

            cursor.execute("""
                ALTER TABLE medicines
                ADD COLUMN note TEXT DEFAULT ''
            """)


# ============================================================
# SOHBET
# ============================================================

def save_chat(chat_type, message, reply):

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
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

        cursor = conn.cursor()

        cursor.execute("""
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

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM messages
            WHERE id = ?
        """, (
            chat_id,
        ))

        return cursor.rowcount > 0


def clear_chats(chat_type="normal"):

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM messages
            WHERE chat_type = ?
        """, (
            chat_type,
        ))

        return cursor.rowcount


# ============================================================
# SAĞLIK KAYITLARI
# ============================================================

def save_health_record(
    symptom,
    medicine,
    note
):

    with db_connection() as conn:

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


def get_health_records():

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM health_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def delete_health_record(record_id):

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
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


def get_period_records():

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM period_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def delete_period_record(record_id):

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM period_records
            WHERE id = ?
        """, (
            record_id,
        ))

        return cursor.rowcount > 0


# ============================================================
# SİNDİRİM / İSHAL
# ============================================================

def save_diarrhea_record(
    date,
    count,
    condition,
    note
):

    with db_connection() as conn:

        cursor = conn.cursor()

        # Sayısal değer geldiyse integer yap
        try:
            count_value = int(count)
        except (ValueError, TypeError):
            count_value = 0

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
            count_value,
            condition,
            note
        ))


def get_diarrhea_records():

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM diarrhea_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def delete_diarrhea_record(record_id):

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
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
    start_date,
    note=""
):

    name = (name or "").strip()
    dose = (dose or "").strip()
    hour = (hour or "").strip()
    start_date = (start_date or "").strip()
    note = (note or "").strip()

    if not name:
        raise ValueError(
            "İlaç adı boş bırakılamaz."
        )

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO medicines
            (
                name,
                dose,
                hour,
                start_date,
                note
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            dose,
            hour,
            start_date,
            note
        ))

        return cursor.lastrowid


def get_medicines():

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
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

        return cursor.fetchall()


def get_medicine(medicine_id):

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM medicines
            WHERE id = ?
        """, (
            medicine_id,
        ))

        return cursor.fetchone()


def update_medicine(
    medicine_id,
    name,
    dose,
    hour,
    start_date,
    note=""
):

    name = (name or "").strip()
    dose = (dose or "").strip()
    hour = (hour or "").strip()
    start_date = (start_date or "").strip()
    note = (note or "").strip()

    if not name:
        raise ValueError(
            "İlaç adı boş bırakılamaz."
        )

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE medicines

            SET
                name = ?,
                dose = ?,
                hour = ?,
                start_date = ?,
                note = ?

            WHERE id = ?
        """, (
            name,
            dose,
            hour,
            start_date,
            note,
            medicine_id
        ))

        return cursor.rowcount > 0


def delete_medicine(medicine_id):

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM medicines
            WHERE id = ?
        """, (
            medicine_id,
        ))

        return cursor.rowcount > 0


# ============================================================
# TÜM VERİLERİ TEMİZLEME
# ============================================================

def clear_all_data():

    with db_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM messages
        """)

        cursor.execute("""
            DELETE FROM health_records
        """)

        cursor.execute("""
            DELETE FROM period_records
        """)

        cursor.execute("""
            DELETE FROM diarrhea_records
        """)

        cursor.execute("""
            DELETE FROM medicines
        """)


# ============================================================
# UYGULAMA BAŞLARKEN VERİTABANINI HAZIRLA
# ============================================================

try:
    init_db()

except Exception as e:

    print(
        "VERİTABANI BAŞLATMA HATASI:",
        repr(e)
        )
