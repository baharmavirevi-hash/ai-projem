import sqlite3
import os


# ============================================================
# DATABASE AYARLARI
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_NAME = os.path.join(
    BASE_DIR,
    "chat.db"
)


# ============================================================
# DATABASE BAĞLANTISI
# ============================================================

def get_db():

    conn = sqlite3.connect(
        DB_NAME
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# DATABASE OLUŞTUR
# ============================================================

def init_db():

    conn = get_db()

    cursor = conn.cursor()

    # ========================================================
    # MAVİGPT SOHBETLERİ
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            chat_type TEXT DEFAULT 'normal',

            message TEXT,

            response TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ========================================================
    # SAĞLIK
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symptom TEXT,

            medicine TEXT,

            note TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ========================================================
    # REGL
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS period_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            start_date TEXT,

            end_date TEXT,

            note TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ========================================================
    # SİNDİRİM
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diarrhea_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT,

            count INTEGER DEFAULT 0,

            condition TEXT,

            note TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ========================================================
    # İLAÇLAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            dose TEXT,

            hour TEXT,

            start_date TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ========================================================
    # AYARLAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            id INTEGER PRIMARY KEY CHECK (id = 1),

            mode TEXT DEFAULT 'normal',

            personality TEXT DEFAULT 'friendly'

        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO settings
        (
            id,
            mode,
            personality
        )

        VALUES
        (
            1,
            'normal',
            'friendly'
        )
    """)

    # ========================================================
    # KULLANICILAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            display_name TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ========================================================
    # ARKADAŞLIKLAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friendships (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            friend_id INTEGER NOT NULL,

            status TEXT DEFAULT 'accepted',

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_id, friend_id),

            FOREIGN KEY(user_id)
                REFERENCES users(id),

            FOREIGN KEY(friend_id)
                REFERENCES users(id)

        )
    """)

    # ========================================================
    # ARKADAŞ MESAJLARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            sender_id INTEGER NOT NULL,

            receiver_id INTEGER NOT NULL,

            message TEXT NOT NULL,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(sender_id)
                REFERENCES users(id),

            FOREIGN KEY(receiver_id)
                REFERENCES users(id)

        )
    """)

    conn.commit()

    conn.close()


# ============================================================
# MAVİGPT SOHBET KAYDET
# ============================================================

def save_chat(
    chat_type,
    message,
    response
):

    conn = get_db()

    conn.execute("""
        INSERT INTO chats
        (
            chat_type,
            message,
            response
        )

        VALUES (?, ?, ?)
    """, (
        chat_type,
        message,
        response
    ))

    conn.commit()

    conn.close()


# ============================================================
# TÜM SOHBET MESAJLARINI GETİR
# ============================================================

def get_chat_messages(
    chat_type="normal"
):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            chat_type,
            message,
            response,
            created_at

        FROM chats

        WHERE chat_type = ?

        ORDER BY id ASC
    """, (
        chat_type,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# SON SOHBETLER
# ============================================================

def get_chats(
    chat_type="normal"
):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            chat_type,
            message,
            response,
            created_at

        FROM chats

        WHERE chat_type = ?

        ORDER BY id DESC
    """, (
        chat_type,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# TEK SOHBET
# ============================================================

def get_chat(
    chat_id
):

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            chat_type,
            message,
            response,
            created_at

        FROM chats

        WHERE id = ?

        LIMIT 1
    """, (
        chat_id,
    )).fetchone()

    conn.close()

    return row


# ============================================================
# ID İLE SOHBET
# ============================================================

def get_chat_by_id(
    chat_id
):

    return get_chat(
        chat_id
    )


# ============================================================
# SOHBET BAŞLIĞINI DÜZENLE
# ============================================================

def update_chat_title(
    chat_id,
    title
):

    conn = get_db()

    conn.execute("""
        UPDATE chats

        SET message = ?

        WHERE id = ?
    """, (
        title,
        chat_id
    ))

    conn.commit()

    conn.close()


# ============================================================
# SOHBET SİL
# ============================================================

def delete_chat(
    chat_id
):

    conn = get_db()

    conn.execute("""
        DELETE FROM chats

        WHERE id = ?
    """, (
        chat_id,
    ))

    conn.commit()

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

    conn.commit()

    conn.close()


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
# REGL
# ============================================================

def save_period_record(
    start_date,
    end_date,
    note
):

    conn = get_db()

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

    conn.commit()

    conn.close()


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
# SİNDİRİM
# ============================================================

def save_diarrhea_record(
    date,
    count,
    condition,
    note
):

    conn = get_db()

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

    conn.commit()

    conn.close()


def get_diarrhea_records():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM diarrhea_records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


# ============================================================
# İLAÇ
# ============================================================

def save_medicine(
    name,
    dose,
    hour,
    start_date
):

    conn = get_db()

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

    conn.commit()

    conn.close()


def get_medicines():

    conn = get_db()

    rows = conn.execute("""
        SELECT *

        FROM medicines

        ORDER BY

            CASE

                WHEN hour IS NULL
                     OR hour = ''

                THEN 1

                ELSE 0

            END,

            hour ASC,

            id DESC

    """).fetchall()

    conn.close()

    return rows


def delete_medicine(
    medicine_id
):

    conn = get_db()

    conn.execute("""
        DELETE FROM medicines

        WHERE id = ?
    """, (
        medicine_id,
    ))

    conn.commit()

    conn.close()


# ============================================================
# AYARLAR
# ============================================================

def get_settings():

    conn = get_db()

    row = conn.execute("""
        SELECT *

        FROM settings

        WHERE id = 1

        LIMIT 1
    """).fetchone()

    conn.close()

    if row:

        return row

    return {
        "mode": "normal",
        "personality": "friendly"
    }


def save_settings(
    mode,
    personality
):

    allowed_modes = {
        "normal",
        "creative",
        "study",
        "concise"
    }

    allowed_personalities = {
        "friendly",
        "funny",
        "serious",
        "teacher"
    }

    if mode not in allowed_modes:

        mode = "normal"

    if personality not in allowed_personalities:

        personality = "friendly"

    conn = get_db()

    conn.execute("""
        UPDATE settings

        SET
            mode = ?,
            personality = ?

        WHERE id = 1
    """, (
        mode,
        personality
    ))

    conn.commit()

    conn.close()


# ============================================================
# KULLANICI OLUŞTUR
# ============================================================

def create_user(
    username,
    display_name=None
):

    username = (
        username or ""
    ).strip().lower()

    display_name = (
        display_name or username
    ).strip()

    if not username:

        return None

    conn = get_db()

    try:

        cursor = conn.execute("""
            INSERT INTO users
            (
                username,
                display_name
            )

            VALUES (?, ?)
        """, (
            username,
            display_name
        ))

        conn.commit()

        user_id = cursor.lastrowid

        conn.close()

        return user_id

    except sqlite3.IntegrityError:

        conn.close()

        return None


# ============================================================
# KULLANICI BUL
# ============================================================

def get_user_by_id(
    user_id
):

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            username,
            display_name,
            created_at

        FROM users

        WHERE id = ?

        LIMIT 1
    """, (
        user_id,
    )).fetchone()

    conn.close()

    return row


def get_user_by_username(
    username
):

    username = (
        username or ""
    ).strip().lower()

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            username,
            display_name,
            created_at

        FROM users

        WHERE username = ?

        LIMIT 1
    """, (
        username,
    )).fetchone()

    conn.close()

    return row


# ============================================================
# ARKADAŞ EKLE
# ============================================================

def add_friend(
    user_id,
    friend_id
):

    if not user_id or not friend_id:

        return False

    if int(user_id) == int(friend_id):

        return False

    conn = get_db()

    try:

        conn.execute("""
            INSERT OR IGNORE INTO friendships
            (
                user_id,
                friend_id,
                status
            )

            VALUES (?, ?, 'accepted')
        """, (
            user_id,
            friend_id
        ))

        conn.execute("""
            INSERT OR IGNORE INTO friendships
            (
                user_id,
                friend_id,
                status
            )

            VALUES (?, ?, 'accepted')
        """, (
            friend_id,
            user_id
        ))

        conn.commit()

        conn.close()

        return True

    except Exception as e:

        print(
            "ARKADAŞ EKLEME HATASI:",
            repr(e)
        )

        conn.close()

        return False


# ============================================================
# ARKADAŞLARI GETİR
# ============================================================

def get_friends(
    user_id
):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            u.id,
            u.username,
            u.display_name,
            u.created_at

        FROM users u

        INNER JOIN friendships f
            ON f.friend_id = u.id

        WHERE
            f.user_id = ?

            AND f.status = 'accepted'

        ORDER BY
            u.display_name COLLATE NOCASE ASC
    """, (
        user_id,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# ARKADAŞLIK KONTROL
# ============================================================

def are_friends(
    user_id,
    friend_id
):

    conn = get_db()

    row = conn.execute("""
        SELECT id

        FROM friendships

        WHERE
            user_id = ?

            AND friend_id = ?

            AND status = 'accepted'

        LIMIT 1
    """, (
        user_id,
        friend_id
    )).fetchone()

    conn.close()

    return row is not None


# ============================================================
# ARKADAŞ MESAJI KAYDET
# ============================================================

def save_friend_message(
    sender_id,
    receiver_id,
    message
):

    message = (
        message or ""
    ).strip()

    if not message:

        return None

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO friend_messages
        (
            sender_id,
            receiver_id,
            message
        )

        VALUES (?, ?, ?)
    """, (
        sender_id,
        receiver_id,
        message
    ))

    conn.commit()

    message_id = cursor.lastrowid

    conn.close()

    return message_id


# ============================================================
# ARKADAŞLA MESAJLARI GETİR
# ============================================================

def get_friend_messages(
    user_id,
    friend_id
):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            fm.id,
            fm.sender_id,
            fm.receiver_id,
            fm.message,
            fm.created_at,

            sender.username
                AS sender_username,

            sender.display_name
                AS sender_name

        FROM friend_messages fm

        LEFT JOIN users sender
            ON sender.id = fm.sender_id

        WHERE
            (
                fm.sender_id = ?
                AND fm.receiver_id = ?
            )

            OR

            (
                fm.sender_id = ?
                AND fm.receiver_id = ?
            )

        ORDER BY
            fm.id ASC
    """, (
        user_id,
        friend_id,
        friend_id,
        user_id
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# ARKADAŞ MESAJLARINI SON MESAJDAN BAŞLATMA
# ============================================================

def get_last_friend_message(
    user_id,
    friend_id
):

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            sender_id,
            receiver_id,
            message,
            created_at

        FROM friend_messages

        WHERE
            (
                sender_id = ?
                AND receiver_id = ?
            )

            OR

            (
                sender_id = ?
                AND receiver_id = ?
            )

        ORDER BY
            id DESC

        LIMIT 1
    """, (
        user_id,
        friend_id,
        friend_id,
        user_id
    )).fetchone()

    conn.close()

    return row


# ============================================================
# DATABASE BAŞLAT
# ============================================================

init_db()
