import sqlite3

DB_NAME = "chat.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Sohbet mesajları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        message TEXT,
        reply TEXT,
        chat_type TEXT DEFAULT 'doctor',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Sağlık kayıtları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symptom TEXT,
        medicine TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Regl kayıtları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS period_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_date TEXT,
        end_date TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # İshal kayıtları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diarrhea_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        count INTEGER,
        condition TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # İlaçlar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dose TEXT,
        hour TEXT,
        start_date TEXT
    )
    """)

    conn.commit()
    conn.close()
