import sqlite3


DB_NAME = "chat.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptom TEXT,
            medicine TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS period_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT,
            end_date TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dose TEXT,
            hour TEXT,
            start_date TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_chat(chat_type, message, reply):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (chat_type, message, reply)
        VALUES (?, ?, ?)
    """, (chat_type, message, reply))

    conn.commit()
    conn.close()


def get_chats(chat_type):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM messages
        WHERE chat_type = ?
        ORDER BY id DESC
    """, (chat_type,))

    data = cursor.fetchall()

    conn.close()

    return data


def save_health_record(symptom, medicine, note):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO health_records
        (symptom, medicine, note)
        VALUES (?, ?, ?)
    """, (symptom, medicine, note))

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

    data = cursor.fetchall()

    conn.close()

    return data


def save_period_record(start_date, end_date, note):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO period_records
        (start_date, end_date, note)
        VALUES (?, ?, ?)
    """, (start_date, end_date, note))

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

    data = cursor.fetchall()

    conn.close()

    return data


def save_diarrhea_record(date, count, condition, note):
    conn = get_db()
    cursor = conn.cursor()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diarrhea_records
        (date, count, condition, note)
        VALUES (?, ?, ?, ?)
    """, (date, count, condition, note))

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

    data = cursor.fetchall()

    conn.close()

    return data


def save_medicine(name, dose, hour, start_date):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO medicines
        (name, dose, hour, start_date)
        VALUES (?, ?, ?, ?)
    """, (name, dose, hour, start_date))

    conn.commit()
    conn.close()


def get_medicines():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM medicines
        ORDER BY hour
    """)

    data = cursor.fetchall()

    conn.close()

    return data

    
