import sqlite3
import os
import secrets
import string

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


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
        DB_NAME,
        timeout=10
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

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

            username TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

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

            sender_id INTEGER NOT NULL,

            receiver_id INTEGER NOT NULL,

            status TEXT DEFAULT 'pending',

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(sender_id, receiver_id),

            FOREIGN KEY(sender_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY(receiver_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # ARKADAŞ SOHBET ODALARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_rooms (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_code TEXT NOT NULL UNIQUE,

            name TEXT DEFAULT 'Arkadaş Sohbeti',

            owner_id INTEGER,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(owner_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        )
    """)

    # ========================================================
    # ODA ÜYELERİ
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_room_members (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_id INTEGER NOT NULL,

            user_id INTEGER NOT NULL,

            joined_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(room_id, user_id),

            FOREIGN KEY(room_id)
                REFERENCES friend_rooms(id)
                ON DELETE CASCADE,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # ARKADAŞ MESAJLARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_id INTEGER NOT NULL,

            user_id INTEGER,

            username TEXT,

            message TEXT,

            photo_path TEXT,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(room_id)
                REFERENCES friend_rooms(id)
                ON DELETE CASCADE,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        )
    """)

    # ========================================================
    # PUSH BİLDİRİM ABONELİKLERİ
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            endpoint TEXT NOT NULL UNIQUE,

            p256dh TEXT NOT NULL,

            auth TEXT NOT NULL,

            created_at
                TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # ========================================================
    # INDEXLER
    # ========================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_chats_type
        ON chats(chat_type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_friend_messages_room
        ON friend_messages(room_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_friendships_sender
        ON friendships(sender_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_friendships_receiver
        ON friendships(receiver_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_room_members_room
        ON friend_room_members(room_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_room_members_user
        ON friend_room_members(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_push_subscriptions_user
        ON push_subscriptions(user_id)
    """)

    conn.commit()
    conn.close()


# ============================================================
# KULLANICI HESABI
# ============================================================

def create_user(
    username,
    password,
    display_name=None
):

    username = (
        username or ""
    ).strip()

    password = password or ""

    if not username or not password:
        return None

    if display_name is None:
        display_name = username

    display_name = (
        display_name.strip()
        if display_name
        else username
    )

    password_hash = generate_password_hash(
        password
    )

    conn = get_db()

    try:

        cursor = conn.execute("""
            INSERT INTO users
            (
                username,
                password_hash,
                display_name
            )

            VALUES (?, ?, ?)
        """, (
            username,
            password_hash,
            display_name
        ))

        conn.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:

        return None

    finally:

        conn.close()


# ============================================================
# KULLANICI ADIYLE KULLANICI BUL
# ============================================================

def get_user_by_username(
    username
):

    username = (
        username or ""
    ).strip()

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            username,
            password_hash,
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
# ID İLE KULLANICI BUL
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


# ============================================================
# ŞİFRE KONTROL
# ============================================================

def check_user_password(
    username,
    password
):

    user = get_user_by_username(
        username
    )

    if not user:
        return None

    if check_password_hash(
        user["password_hash"],
        password
    ):
        return user

    return None


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
# MAVİGPT MESAJLARINI GETİR
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
# SOHBET BAŞLIĞI DÜZENLE
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
# SAĞLIK KAYDI KAYDET
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
# REGL KAYDI KAYDET
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
# SİNDİRİM KAYDI KAYDET
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


# ============================================================
# SİNDİRİM KAYITLARINI GETİR
# ============================================================

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
# İLAÇ KAYDET
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


# ============================================================
# İLAÇLARI GETİR
# ============================================================

def get_medicines():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM medicines
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


# ============================================================
# İLAÇ SİL
# ============================================================

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
# AYARLARI KAYDET
# ============================================================

def save_settings(
    mode,
    personality
):

    conn = get_db()

    conn.execute("""
        INSERT OR REPLACE INTO settings
        (
            id,
            mode,
            personality
        )

        VALUES
        (
            1,
            ?,
            ?
        )
    """, (
        mode,
        personality
    ))

    conn.commit()
    conn.close()


# ============================================================
# AYARLARI GETİR
# ============================================================

def get_settings():

    conn = get_db()

    row = conn.execute("""
        SELECT
            mode,
            personality

        FROM settings

        WHERE id = 1

        LIMIT 1
    """).fetchone()

    conn.close()

    if not row:

        return {
            "mode": "normal",
            "personality": "friendly"
        }

    return row


# ============================================================
# ARKADAŞLIK İSTEĞİ GÖNDER
# ============================================================

def send_friend_request(
    sender_id,
    receiver_id
):

    if not sender_id or not receiver_id:
        return False

    if sender_id == receiver_id:
        return False

    conn = get_db()

    try:

        existing = conn.execute("""
            SELECT
                id,
                status

            FROM friendships

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

            LIMIT 1
        """, (
            sender_id,
            receiver_id,
            receiver_id,
            sender_id
        )).fetchone()

        if existing:
            return False

        conn.execute("""
            INSERT INTO friendships
            (
                sender_id,
                receiver_id,
                status
            )

            VALUES (?, ?, 'pending')
        """, (
            sender_id,
            receiver_id
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# ============================================================
# ARKADAŞLIK İSTEĞİNİ KABUL ET
# ============================================================

def accept_friend_request(
    request_id,
    user_id
):

    conn = get_db()

    cursor = conn.execute("""
        UPDATE friendships

        SET status = 'accepted'

        WHERE
            id = ?
            AND receiver_id = ?
            AND status = 'pending'
    """, (
        request_id,
        user_id
    ))

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    return success


# ============================================================
# ARKADAŞLIK İSTEĞİNİ REDDET
# ============================================================

def reject_friend_request(
    request_id,
    user_id
):

    conn = get_db()

    cursor = conn.execute("""
        UPDATE friendships

        SET status = 'rejected'

        WHERE
            id = ?
            AND receiver_id = ?
            AND status = 'pending'
    """, (
        request_id,
        user_id
    ))

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    return success


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
            u.display_name

        FROM users u

        INNER JOIN friendships f
            ON
            (
                f.sender_id = ?
                AND f.receiver_id = u.id
            )
            OR
            (
                f.receiver_id = ?
                AND f.sender_id = u.id
            )

        WHERE f.status = 'accepted'

        ORDER BY
            COALESCE(
                u.display_name,
                u.username
            ) ASC
    """, (
        user_id,
        user_id
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# GELEN ARKADAŞLIK İSTEKLERİ
# ============================================================

def get_pending_friend_requests(
    user_id
):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            f.id,
            f.sender_id,
            f.receiver_id,
            f.status,
            f.created_at,

            u.username,
            u.display_name

        FROM friendships f

        INNER JOIN users u
            ON u.id = f.sender_id

        WHERE
            f.receiver_id = ?
            AND f.status = 'pending'

        ORDER BY f.id DESC
    """, (
        user_id,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# ARKADAŞLIK KONTROL
# ============================================================

def are_friends(
    user_a,
    user_b
):

    conn = get_db()

    row = conn.execute("""
        SELECT id

        FROM friendships

        WHERE
            status = 'accepted'
            AND
            (
                (
                    sender_id = ?
                    AND receiver_id = ?
                )
                OR
                (
                    sender_id = ?
                    AND receiver_id = ?
                )
            )

        LIMIT 1
    """, (
        user_a,
        user_b,
        user_b,
        user_a
    )).fetchone()

    conn.close()

    return row is not None


# ============================================================
# ARKADAŞ ODASI KODU ÜRET
# ============================================================

def generate_room_code(
    length=6
):

    alphabet = (
        string.ascii_uppercase
        + string.digits
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


# ============================================================
# ARKADAŞ ODASI OLUŞTUR
# ============================================================

def create_friend_room(
    room_name="Arkadaş Sohbeti",
    owner_id=None
):

    conn = get_db()

    for _ in range(20):

        room_code = generate_room_code()

        try:

            cursor = conn.execute("""
                INSERT INTO friend_rooms
                (
                    room_code,
                    name,
                    owner_id
                )

                VALUES (?, ?, ?)
            """, (
                room_code,
                room_name or "Arkadaş Sohbeti",
                owner_id
            ))

            room_id = cursor.lastrowid

            if owner_id:

                conn.execute("""
                    INSERT OR IGNORE INTO
                    friend_room_members
                    (
                        room_id,
                        user_id
                    )

                    VALUES (?, ?)
                """, (
                    room_id,
                    owner_id
                ))

            conn.commit()

            conn.close()

            return room_code

        except sqlite3.IntegrityError:

            continue

    conn.close()

    return None


# ============================================================
# ARKADAŞ ODASI BUL
# ============================================================

def get_friend_room(
    room_code
):

    room_code = (
        room_code or ""
    ).strip().upper()

    conn = get_db()

    row = conn.execute("""
        SELECT
            id,
            room_code,
            name,
            owner_id,
            created_at

        FROM friend_rooms

        WHERE room_code = ?

        LIMIT 1
    """, (
        room_code,
    )).fetchone()

    conn.close()

    return row


# ============================================================
# KULLANICIYI ODAYA EKLE
# ============================================================

def join_friend_room(
    room_code,
    user_id
):

    room = get_friend_room(
        room_code
    )

    if not room or not user_id:
        return False

    conn = get_db()

    try:

        cursor = conn.execute("""
            INSERT OR IGNORE INTO
            friend_room_members
            (
                room_id,
                user_id
            )

            VALUES (?, ?)
        """, (
            room["id"],
            user_id
        ))

        conn.commit()

        return cursor.rowcount > 0 or is_room_member(
            room_code,
            user_id
        )

    finally:

        conn.close()


# ============================================================
# KULLANICI ODADA MI?
# ============================================================

def is_room_member(
    room_code,
    user_id
):

    room = get_friend_room(
        room_code
    )

    if not room:
        return False

    if not user_id:
        return False

    conn = get_db()

    row = conn.execute("""
        SELECT id

        FROM friend_room_members

        WHERE
            room_id = ?
            AND user_id = ?

        LIMIT 1
    """, (
        room["id"],
        user_id
    )).fetchone()

    conn.close()

    return row is not None


# ============================================================
# ODA ÜYELERİ
# ============================================================

def get_friend_room_members(
    room_code
):

    room = get_friend_room(
        room_code
    )

    if not room:
        return []

    conn = get_db()

    rows = conn.execute("""
        SELECT
            u.id,
            u.username,
            u.display_name,
            m.joined_at

        FROM friend_room_members m

        INNER JOIN users u
            ON u.id = m.user_id

        WHERE m.room_id = ?

        ORDER BY m.joined_at ASC
    """, (
        room["id"],
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# KULLANICININ ARKADAŞ ODALARINI GETİR
# ============================================================

def get_user_friend_rooms(
    user_id
):

    if not user_id:
        return []

    conn = get_db()

    rows = conn.execute("""
        SELECT DISTINCT
            r.id,
            r.room_code,
            r.name,
            r.owner_id,
            r.created_at

        FROM friend_rooms r

        INNER JOIN friend_room_members m
            ON m.room_id = r.id

        WHERE m.user_id = ?

        ORDER BY r.id DESC
    """, (
        user_id,
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# ARKADAŞ MESAJI KAYDET
# ============================================================

def save_friend_message(
    room_code,
    username,
    message,
    user_id=None,
    photo_path=None
):

    room = get_friend_room(
        room_code
    )

    if not room:
        return False

    if not message and not photo_path:
        return False

    if not user_id:
        return False

    conn = get_db()

    try:

        # ----------------------------------------------------
        # ÖNEMLİ:
        # Kullanıcı gerçekten odanın üyesi olmalı.
        # ----------------------------------------------------

        member = conn.execute("""
            SELECT id

            FROM friend_room_members

            WHERE
                room_id = ?
                AND user_id = ?

            LIMIT 1
        """, (
            room["id"],
            user_id
        )).fetchone()

        if not member:

            return False

        # ----------------------------------------------------
        # MESAJI KAYDET
        # ----------------------------------------------------

        conn.execute("""
            INSERT INTO friend_messages
            (
                room_id,
                user_id,
                username,
                message,
                photo_path
            )

            VALUES (?, ?, ?, ?, ?)
        """, (
            room["id"],
            user_id,
            username or "Misafir",
            message or "",
            photo_path
        ))

        conn.commit()

        return True

    except Exception as e:

        print(
            "ARKADAŞ MESAJI DATABASE HATASI:",
            repr(e)
        )

        return False

    finally:

        conn.close()


# ============================================================
# ARKADAŞ MESAJLARINI GETİR
# ============================================================

def get_friend_messages(
    room_code,
    limit=200
):

    room = get_friend_room(
        room_code
    )

    if not room:
        return []

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 200

    if limit <= 0:
        limit = 200

    if limit > 500:
        limit = 500

    conn = get_db()

    rows = conn.execute("""
        SELECT
            fm.id,
            fm.room_id,
            fm.user_id,
            fm.username,
            fm.message,
            fm.photo_path,
            fm.created_at,

            u.display_name

        FROM friend_messages fm

        LEFT JOIN users u
            ON u.id = fm.user_id

        WHERE fm.room_id = ?

        ORDER BY fm.id ASC

        LIMIT ?
    """, (
        room["id"],
        limit
    )).fetchall()

    conn.close()

    return rows


# ============================================================
# FOTOĞRAFLI MESAJ KAYDET
# ============================================================

def save_friend_photo_message(
    room_code,
    username,
    photo_path,
    user_id=None
):

    if not photo_path:
        return False

    return save_friend_message(
        room_code=room_code,
        username=username,
        message="",
        user_id=user_id,
        photo_path=photo_path
    )


# ============================================================
# ARKADAŞ ODASI SİL
# ============================================================

def delete_friend_room(
    room_code,
    user_id=None
):

    room = get_friend_room(
        room_code
    )

    if not room:
        return False

    if user_id:

        if room["owner_id"] != user_id:
            return False

    conn = get_db()

    cursor = conn.execute("""
        DELETE FROM friend_rooms

        WHERE id = ?
    """, (
        room["id"],
    ))

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    return success


# ============================================================
# PUSH BİLDİRİM ABONELİĞİ KAYDET
# ============================================================

def save_push_subscription(
    endpoint,
    p256dh,
    auth,
    user_id=None
):

    endpoint = (
        endpoint or ""
    ).strip()

    p256dh = (
        p256dh or ""
    ).strip()

    auth = (
        auth or ""
    ).strip()

    if not endpoint or not p256dh or not auth:
        return False

    conn = get_db()

    try:

        existing = conn.execute("""
            SELECT id

            FROM push_subscriptions

            WHERE endpoint = ?

            LIMIT 1
        """, (
            endpoint,
        )).fetchone()

        if existing:

            conn.execute("""
                UPDATE push_subscriptions

                SET
                    user_id = ?,
                    p256dh = ?,
                    auth = ?

                WHERE endpoint = ?
            """, (
                user_id,
                p256dh,
                auth,
                endpoint
            ))

        else:

            conn.execute("""
                INSERT INTO push_subscriptions
                (
                    user_id,
                    endpoint,
                    p256dh,
                    auth
                )

                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                endpoint,
                p256dh,
                auth
            ))

        conn.commit()

        return True

    except Exception as e:

        print(
            "PUSH ABONELİĞİ KAYIT HATASI:",
            repr(e)
        )

        return False

    finally:

        conn.close()


# ============================================================
# PUSH BİLDİRİM ABONELİKLERİNİ GETİR
# ============================================================

def get_push_subscriptions(
    user_id=None
):

    conn = get_db()

    if user_id is None:

        rows = conn.execute("""
            SELECT
                id,
                user_id,
                endpoint,
                p256dh,
                auth,
                created_at

            FROM push_subscriptions

            ORDER BY id DESC
        """).fetchall()

    else:

        rows = conn.execute("""
            SELECT
                id,
                user_id,
                endpoint,
                p256dh,
                auth,
                created_at

            FROM push_subscriptions

            WHERE user_id = ?

            ORDER BY id DESC
        """, (
            user_id,
        )).fetchall()

    conn.close()

    return rows


# ============================================================
# PUSH ABONELİĞİ SİL
# ============================================================

def delete_push_subscription(
    endpoint
):

    endpoint = (
        endpoint or ""
    ).strip()

    if not endpoint:
        return False

    conn = get_db()

    cursor = conn.execute("""
        DELETE FROM push_subscriptions

        WHERE endpoint = ?
    """, (
        endpoint,
    ))

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    return success


# ============================================================
# DATABASE BAŞLAT
# ============================================================

init_db()

