def init_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        chat_type TEXT,

        user_message TEXT,

        ai_message TEXT

    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_records(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symptom TEXT,

        medicine TEXT,

        note TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS period_records(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        start_date TEXT,

        end_date TEXT,

        note TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

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
    def save_medicine(name, dose, hour, start_date):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO medicines
    (name, dose, hour, start_date)

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

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *

    FROM medicines

    ORDER BY hour
    """)

    data = cursor.fetchall()

    conn.close()

    return data
