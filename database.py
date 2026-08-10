import sqlite3

DB_NAME = "chat.db"


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
    # REGL
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
    # SİNDİRİM
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

    # --------------------------------------------------------
    # AYARLAR
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            theme TEXT DEFAULT 'light',
            personality TEXT DEFAULT 'friendly',
            response_style TEXT DEFAULT 'normal'
        )
    """)

    # İlk ayar kaydı yoksa oluştur
    cursor.execute("""
        INSERT OR IGNORE INTO settings
        (id, theme, personality, response_style)
        VALUES (1, 'light', 'friendly', 'normal')
    """)

    conn.commit()
    conn.close()


# ============================================================
# SOHBET KAYDET
# ============================================================

def save_chat(chat_type, message, response):

    conn = get_db()

    conn.execute("""
        INSERT INTO chats
        (chat_type, message, response)
        VALUES (?, ?, ?)
    """, (
        chat_type,
        message,
        response
    ))

    conn.commit()
    conn.close()


# ============================================================
# SOHBETLERİ GETİR
# ============================================================

def get_chats(chat_type="normal"):

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM chats
        WHERE chat_type = ?
        ORDER BY id DESC
    """, (
        chat_type,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# TEK SOHBET GETİR
# ============================================================

def get_chat(chat_id):

    conn = get_db()

    row = conn.execute("""
        SELECT *
        FROM chats
        WHERE id = ?
        LIMIT 1
    """, (
        chat_id,
    )).fetchone()

    conn.close()

    return row


# Eski isim de çalışmaya devam etsin
def get_chat_by_id(chat_id):
    return get_chat(chat_id)


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
        (symptom, medicine, note)
        VALUES (?, ?, ?)
    """, (
        symptom,
        medicine,
        note
    ))

    conn.commit()
    conn.close()


# ============================================================
# SAĞLIK KAYITLARINI GETİR
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
        (start_date, end_date, note)
        VALUES (?, ?, ?)
    """, (
        start_date,
        end_date,
        note
    ))

    conn.commit()
    conn.close()


# ============================================================
# REGL KAYITLARINI GETİR
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

   
