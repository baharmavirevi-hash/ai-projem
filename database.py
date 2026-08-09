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
    conn = sqlite3.connect(
        DB_NAME,
        timeout=10
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# DATABASE OLUŞTURMA
# ============================================================

def init_db():

    conn = get_db()

    try:

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

        conn.commit()

        print("DATABASE HAZIR:", DB_NAME)

    except Exception as e:

        conn.rollback()

        print(
            "DATABASE INIT HATASI:",
            repr(e)
        )

        raise

    finally:

        conn.close()


# ============================================================
# SOHBET
# ============================================================

def save_chat(chat_type, message, reply):

    conn = get_db()

    try:

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

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "SOHBET KAYDETME HATASI:",
            repr(e)
        )

        raise

    finally:

        conn.close()


def get_chats(chat_type):

    conn = get_db()

    try:

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

    except Exception as e:

        print(
            "SOHBETLERİ OKUMA HATASI:",
            repr(e)
        )

        return []

    finally:

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

    try:

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

    except Exception as e:

        conn.rollback()

        print(
            "SAĞLIK KAYDETME HATASI:",
            repr(e)
        )

        raise

    finally:

        conn.close()


def get_health_records():

    conn = get_db()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM health_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    except Exception as e:

        print(
            "SAĞLIK KAYITLARINI OKUMA HATASI:",
            repr(e)
        )

        return []

    finally:

        conn.close()


# ============================================================
# REGL
# ============================================================

def save_period_record(
    start_date,
    end_date,
    note
):

    conn = get_db()

    try:

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

    except Exception as e:

        conn.rollback()

        print(
            "REGL KAYDETME HATASI:",
            repr(e)
        )

        raise

    finally:

        conn.close()


def get_period_records():

    conn = get_db()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM period_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    except Exception as e:

        print(
            "REGL KAYITLARINI OKUMA HATASI:",
            repr(e)
        )

        return []

    finally:

        conn.close()


# ============================================================
# SİNDİRİM / İSHAL
# ============================================================

def save_diarrhea_record(
    date,
    count,
    condition,
    note
):

    conn = get_db()

    try:

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

    except Exception as e:

        conn.rollback()

        print(
            "SİNDİRİM KAYDETME HATASI:",
            repr(e)
        )

        raise

    finally:

        conn.close()


def get_diarrhea_records():

    conn = get_db()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM diarrhea_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    except Exception as e:

        print(
            "SİNDİRİM KAYITLARINI OKUMA HATASI:",
            repr(e)
        )

        return []

    finally:

        conn.close()


# ============================================================
# İLAÇ EKLE
# ============================================================

def save_medicine(
    name,
    dose,
    hour,
    start_date
):

    conn = get_db()

    try:

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

    except Exception as e:

        conn.rollback()

        print(
            "İLAÇ KAYDETME HATASI:",
            repr(e)
        )

        raise

    finally:

        conn.close()


# ============================================================
# İLAÇLARI GETİR
# ============================================================

def get_medicines():

    conn = get_db()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM medicines
            ORDER BY
                CASE
                    WHEN hour IS NULL OR hour = ''
                    THEN 1
