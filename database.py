import sqlite3

DB_NAME = "chat.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot TEXT,
        title TEXT,
        message TEXT,
        answer TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_chat(bot, message, answer):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    title = message[:30]

    c.execute("""
    INSERT INTO chats(bot, title, message, answer)
    VALUES (?, ?, ?, ?)
    """, (bot, title, message, answer))

    conn.commit()
    conn.close()


def get_chats(bot):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    SELECT id, title
    FROM chats
    WHERE bot=?
    ORDER BY id DESC
    """, (bot,))

    rows = c.fetchall()

    conn.close()

    return rows


def get_chat(chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM chats
    WHERE id=?
    """, (chat_id,))

    row = c.fetchone()

    conn.close()

    return row


def delete_chat(chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    DELETE FROM chats
    WHERE id=?
    """, (chat_id,))

    conn.commit()
    conn.close()


init_db()
