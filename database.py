import sqlite3


DB_NAME = "mavigpt.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_type TEXT,
        message TEXT,
        answer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_chat(chat_type, message, answer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chats(chat_type, message, answer)
    VALUES (?, ?, ?)
    """, (chat_type, message, answer))

    conn.commit()
    conn.close()


def get_chats(chat_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, message, answer
    FROM chats
    WHERE chat_type = ?
    ORDER BY id DESC
    """, (chat_type,))

    chats = cursor.fetchall()

    conn.close()

    return chats


def delete_chat(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chats WHERE id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()
