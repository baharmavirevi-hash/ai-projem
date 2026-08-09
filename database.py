import os
import sqlite3
from contextlib import closing

# =========================================================
# MAVİGPT - DATABASE
# =========================================================
#
# Railway:
#   Volume bağlandıysa veritabanı /data/chat.db olur.
#
# Yerel bilgisayarda:
#   Proje klasöründeki chat.db kullanılır.
#
# Böylece kod hem Railway hem de bilgisayarda çalışabilir.
# =========================================================


# Railway Volume için önerilen klasör
RAILWAY_DATA_DIR = "/data"

# /data mevcut ve yazılabiliyorsa onu kullan.
# Değilse uygulamanın bulunduğu klasörü kullan.
if os.path.isdir(RAILWAY_DATA_DIR) and os.access(RAILWAY_DATA_DIR, os.W_OK):
    DB_DIR = RAILWAY_DATA_DIR
else:
    DB_DIR = os.path.dirname(os.path.abspath(__file__))


# Klasör yoksa oluştur
os.makedirs(DB_DIR, exist_ok=True)

# Veritabanı dosyasının tam yolu
DB_NAME = os.path.join(DB_DIR, "chat.db")


# =========================================================
# DATABASE BAĞLANTISI
# =========================================================

def get_db():
    """
    SQLite bağlantısı oluşturur.

    Row factory sayesinde:
        kayit["message"]
        kayit["reply"]

    gibi okunabilir şekilde veri alabiliriz.
    """

    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    # SQLite'ın daha güvenli ve dayanıklı çalışması için
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")

    # WAL modu aynı anda okuma/yazma sırasında
    # SQLite'ın daha stabil çalışmasına yardımcı olur.
    conn.execute("PRAGMA journal_mode = WAL")

    return conn


# =========================================================
# DATABASE BAŞLATMA
# =========================================================

def init_db():
    """
    Bütün tabloları oluşturur.

    CREATE TABLE IF NOT EXISTS kullanıldığı için
    mevcut kayıtlar silinmez.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        # -------------------------------------------------
        # SOHBET MESAJLARI
        # -------------------------------------------------

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

        # -------------------------------------------------
        # SAĞLIK KAYITLARI
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symptom TEXT,
                medicine TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -------------------------------------------------
        # REGL KAYITLARI
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS period_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT,
                end_date TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -------------------------------------------------
        # SİNDİRİM / İSHAL KAYITLARI
        # -------------------------------------------------

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

        # -------------------------------------------------
        # İLAÇLAR
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                dose TEXT,
                hour TEXT,
                start_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -------------------------------------------------
        # ESKİ DATABASE UYUMLULUĞU
        # -------------------------------------------------
        #
        # Eğer medicines tablosu eski sürümden geldiyse
        # created_at sütunu bulunmayabilir.
        #
        # Bu yüzden eksik sütunları kontrol ediyoruz.
        # -------------------------------------------------

        cursor.execute("PRAGMA table_info(medicines)")
        medicine_columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        if "created_at" not in medicine_columns:
            cursor.execute("""
                ALTER TABLE medicines
                ADD COLUMN created_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)

        conn.commit()

    finally:
        conn.close()


# =========================================================
# SOHBET
# =========================================================

def save_chat(chat_type, message, reply):
    """
    Bir sohbet mesajını kaydeder.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages
            (
                user,
                message,
                reply,
                chat_type
            )
            VALUES (?, ?, ?, ?)
        """, (
            "user",
            message or "",
            reply or "",
            chat_type or "normal"
        ))

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def get_chats(chat_type="normal"):
    """
    Belirli bir sohbet türündeki mesajları getirir.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM messages
            WHERE chat_type = ?
            ORDER BY id DESC
        """, (
            chat_type or "normal",
        ))

        return cursor.fetchall()

    finally:
        conn.close()


def get_all_chats():
    """
    Bütün sohbetleri getirir.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM messages
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()


# =========================================================
# SAĞLIK
# =========================================================

def save_health_record(symptom="", medicine="", note=""):
    """
    Sağlık kaydı oluşturur.
    """

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
            symptom or "",
            medicine or "",
            note or ""
        ))

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def get_health_records():
    """
    Sağlık kayıtlarını yeni kayıttan eski kayda doğru getirir.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM health_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()


# =========================================================
# REGL
# =========================================================

def save_period_record(start_date="", end_date="", note=""):
    """
    Regl kaydı oluşturur.
    """

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
            start_date or "",
            end_date or "",
            note or ""
        ))

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def get_period_records():
    """
    Regl kayıtlarını getirir.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM period_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()


# =========================================================
# SİNDİRİM / İSHAL
# =========================================================

def save_diarrhea_record(
    date="",
    count=0,
    condition="",
    note=""
):
    """
    Sindirim kaydı oluşturur.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        # count değerini güvenli şekilde integer'a çevirmeye çalış.
        try:
            count_value = int(count)
        except (TypeError, ValueError):
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
            date or "",
            count_value,
            condition or "",
            note or ""
        ))

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def get_diarrhea_records():
    """
    Sindirim kayıtlarını getirir.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM diarrhea_records
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()


# =========================================================
# İLAÇ
# =========================================================

def save_medicine(
    name="",
    dose="",
    hour="",
    start_date=""
):
    """
    İlaç kaydı oluşturur.
    """

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
            name or "",
            dose or "",
            hour or "",
            start_date or ""
        ))

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def get_medicines():
    """
    İlaçları saat sırasına göre getirir.
    """

    conn = get_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM medicines
            ORDER BY hour ASC, id DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()


# =========================================================
# TEKİL KAYIT SİLME
# =========================================================

def delete_health_record(record_id):
    conn = get_db()

    try:
        conn.execute(
            "DELETE FROM health_records WHERE id = ?",
            (record_id,)
        )

        conn.commit()

    finally:
        conn.close()


def delete_period_record(record_id):
    conn = get_db()

    try:
        conn.execute(
            "DELETE FROM period_records WHERE id = ?",
            (record_id,)
        )

        conn.commit()

    finally:
        conn.close()


def delete_diarrhea_record(record_id):
    conn = get_db()

    try:
        conn.execute(
            "DELETE FROM diarrhea_records WHERE id = ?",
            (record_id,)
        )

        conn.commit()

    finally:
        conn.close()


def delete_medicine(record_id):
    conn = get_db()

    try:
        conn.execute(
            "DELETE FROM medicines WHERE id = ?",
            (record_id,)
        )

        conn.commit()

    finally:
        conn.close()


# =========================================================
# DATABASE DURUMU
# =========================================================

def database_info():
    """
    Veritabanının nerede olduğunu kontrol etmek için.
    """

    return {
        "database_path": DB_NAME,
        "database_exists": os.path.exists(DB_NAME),
        "database_size": (
            os.path.getsize(DB_NAME)
            if os.path.exists(DB_NAME)
            else 0
        )
    }


# =========================================================
# OTOMATİK BAŞLAT
# =========================================================

init_db()

