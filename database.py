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
        chat_type TEXT,
        user_message TEXT,
        ai_message TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_chat(chat_type, user_message, ai_message):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO messages
    (chat_type, user_message, ai_message)
    VALUES (?, ?, ?)
    """, (
        chat_type,
        user_message,
        ai_message
    ))

    conn.commit()
    conn.close()


def get_chats(chat_type):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM messages
    WHERE chat_type = ?
    ORDER BY id DESC
    """, (chat_type,))

    chats = cursor.fetchall()

    conn.close()

    return chats
