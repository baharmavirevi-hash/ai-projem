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
# TÜM MAVİGPT MESAJLARINI GETİR
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
# SOHBET BAŞLIĞINI / MESAJINI DÜZENLE
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
# 3. BÖLÜM — ANA SAYFA / MAVİGPT
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    mesaj = ""
    cevap = ""
    filename = None

    # --------------------------------------------------------
    # SOHBETLERİ GETİR
    # --------------------------------------------------------

    try:

        sohbetler = get_chats(
            "normal"
        )

    except Exception as e:

        print(
            "SOHBET OKUMA HATASI:",
            repr(e)
        )

        sohbetler = []

    # --------------------------------------------------------
    # MESAJ GEÇMİŞİNİ GETİR
    # --------------------------------------------------------

    try:

        mesajlar = get_chat_messages(
            "normal"
        )

    except Exception as e:

        print(
            "MESAJ GEÇMİŞİ HATASI:",
            repr(e)
        )

        mesajlar = []

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        mesaj = request.form.get(
            "mesaj",
            ""
        ).strip()

        # ----------------------------------------------------
        # FOTOĞRAF
        # ----------------------------------------------------

        foto, filename = upload_photo(
            app
        )

        # ----------------------------------------------------
        # MESAJ VEYA FOTOĞRAF VARSA
        # ----------------------------------------------------

        if mesaj or foto:

            if mesaj:

                ai_mesaj = mesaj

            else:

                ai_mesaj = (
                    "Bu fotoğrafı incele ve "
                    "genel, güvenli bilgi ver."
                )

            # ------------------------------------------------
            # ÖNCEKİ KONUŞMALAR
            # ------------------------------------------------

            try:

                history = get_chat_messages(
                    "normal"
                )

            except Exception as e:

                print(
                    "HAFIZA OKUMA HATASI:",
                    repr(e)
                )

                history = []

            # ------------------------------------------------
            # MAVİGPT CEVABI
            # ------------------------------------------------

            cevap = ask_mavigpt(
                ai_mesaj,
                foto,
                history
            )

            # ------------------------------------------------
            # VERİTABANINA KAYDET
            # ------------------------------------------------

            try:

                save_chat(
                    "normal",
                    mesaj if mesaj else "Fotoğraf",
                    cevap
                )

            except Exception as e:

                print(
                    "SOHBET KAYIT HATASI:",
                    repr(e)
                )

            # ------------------------------------------------
            # LİSTEYİ YENİLE
            # ------------------------------------------------

            try:

                mesajlar = get_chat_messages(
                    "normal"
                )

                sohbetler = get_chats(
                    "normal"
                )

            except Exception as e:

                print(
                    "SOHBET YENİLEME HATASI:",
                    repr(e)
                )

    # --------------------------------------------------------
    # SAYFAYI GÖSTER
    # --------------------------------------------------------

    return render_template(
        "mavigpt.html",

        mesaj=mesaj,

        cevap=cevap,

        foto_url=get_photo_url(
            filename
        ),

        mesajlar=mesajlar,

        sohbetler=sohbetler
    )


# ============================================================
# TEK SOHBET
# ============================================================

@app.route(
    "/chat/<int:chat_id>"
)
def chat(chat_id):

    sohbet = get_chat(
        chat_id
    )

    if not sohbet:

        return redirect(
            url_for("home")
        )

    return render_template(
        "chat.html",

        sohbet=sohbet
    )


# ============================================================
# SOHBET BAŞLIĞI DÜZENLE
# ============================================================

@app.route(
    "/chat/edit/<int:chat_id>",
    methods=["POST"]
)
def chat_edit(chat_id):

    title = request.form.get(
        "title",
        ""
    ).strip()

    if title:

        try:

            update_chat_title(
                chat_id,
                title
            )

        except Exception as e:

            print(
                "SOHBET DÜZENLEME HATASI:",
                repr(e)
            )

    return redirect(
        url_for(
            "chat",
            chat_id=chat_id
        )
    )


# ============================================================
# SOHBET SİL
# ============================================================

@app.route(
    "/chat/delete/<int:chat_id>",
    methods=["POST"]
)
def chat_delete(chat_id):

    try:

        delete_chat(
            chat_id
        )

    except Exception as e:

        print(
            "SOHBET SİLME HATASI:",
            repr(e)
        )

    return redirect(
        url_for("home")
    )
    # ============================================================
# 4. BÖLÜM — CEBİMDEKİ DOKTOR
# ============================================================

@app.route(
    "/doctor",
    methods=["GET", "POST"]
)
def doctor():

    mesaj = None
    cevap = None
    filename = None
    kayit_mesaji = None

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        mesaj = request.form.get(
            "mesaj",
            ""
        ).strip()

        symptom = request.form.get(
            "symptom",
            ""
        ).strip()

        medicine = request.form.get(
            "medicine",
            ""
        ).strip()

        note = request.form.get(
            "note",
            ""
        ).strip()

        # ----------------------------------------------------
        # SAĞLIK KAYDI
        # ----------------------------------------------------

        if symptom or medicine or note:

            try:

                save_health_record(
                    symptom,
                    medicine,
                    note
                )

                kayit_mesaji = (
                    "✅ Sağlık kaydın kaydedildi."
                )

            except Exception as e:

                print(
                    "SAĞLIK KAYIT HATASI:",
                    repr(e)
                )

                kayit_mesaji = (
                    "❌ Sağlık kaydı kaydedilemedi."
                )

        # ----------------------------------------------------
        # FOTOĞRAF
        # ----------------------------------------------------

        foto, filename = upload_photo(
            app
        )

        # ----------------------------------------------------
        # MAVİGPT
        # ----------------------------------------------------

        if mesaj or foto:

            ai_mesaj = mesaj or (
                "Bu sağlık fotoğrafı hakkında "
                "genel ve güvenli bilgi ver. "
                "Kesin tanı koyma."
            )

            cevap = ask_mavigpt(
                ai_mesaj,
                foto
            )

    # --------------------------------------------------------
    # SAĞLIK KAYITLARINI GETİR
    # --------------------------------------------------------

    try:

        kayitlar = get_health_records()

    except Exception as e:

        print(
            "SAĞLIK OKUMA HATASI:",
            repr(e)
        )

        kayitlar = []

    # --------------------------------------------------------
    # SAYFAYI GÖSTER
    # --------------------------------------------------------

    return render_template(
        "doctor.html",

        mesaj=mesaj,

        cevap=cevap,

        kayitlar=kayitlar,

        kayit_mesaji=kayit_mesaji,

        foto_url=get_photo_url(
            filename
        )
    )
    # ============================================================
# 5. BÖLÜM — REGL TAKİBİ
# ============================================================

@app.route(
    "/period",
    methods=["GET", "POST"]
)
def period():

    kayit_mesaji = None

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        start = request.form.get(
            "start_date",
            ""
        ).strip()

        end = request.form.get(
            "end_date",
            ""
        ).strip()

        note = request.form.get(
            "note",
            ""
        ).strip()

        # ----------------------------------------------------
        # KAYDET
        # ----------------------------------------------------

        if start:

            try:

                save_period_record(
                    start,
                    end,
                    note
                )

                kayit_mesaji = (
                    "✅ Regl kaydın kaydedildi."
                )

            except Exception as e:

                print(
                    "REGL KAYIT HATASI:",
                    repr(e)
                )

                kayit_mesaji = (
                    "❌ Regl kaydı kaydedilemedi."
                )

    # --------------------------------------------------------
    # KAYITLARI GETİR
    # --------------------------------------------------------

    try:

        kayitlar = get_period_records()

    except Exception as e:

        print(
            "REGL OKUMA HATASI:",
            repr(e)
        )

        kayitlar = []

    # --------------------------------------------------------
    # SAYFAYI GÖSTER
    # --------------------------------------------------------

    return render_template(
        "period.html",

        kayitlar=kayitlar,

        kayit_mesaji=kayit_mesaji
    )
    # ============================================================
# 6. BÖLÜM — SİNDİRİM TAKİBİ
# ============================================================

@app.route(
    "/diarrhea",
    methods=["GET", "POST"]
)
def diarrhea():

    kayit_mesaji = None

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        date = request.form.get(
            "date",
            ""
        ).strip()

        count_raw = request.form.get(
            "count",
            ""
        ).strip()

        condition = request.form.get(
            "condition",
            ""
        ).strip()

        note = request.form.get(
            "note",
            ""
        ).strip()

        # ----------------------------------------------------
        # SAYIYI KONTROL ET
        # ----------------------------------------------------

        try:

            count = max(
                0,
                int(count_raw or 0)
            )

        except (
            ValueError,
            TypeError
        ):

            count = 0

        # ----------------------------------------------------
        # KAYIT VARSA KAYDET
        # ----------------------------------------------------

        if (
            date
            or count
            or condition
            or note
        ):

            try:

                save_diarrhea_record(
                    date,
                    count,
                    condition,
                    note
                )

                kayit_mesaji = (
                    "✅ Sindirim kaydın kaydedildi."
                )

            except Exception as e:

                print(
                    "SİNDİRİM KAYIT HATASI:",
                    repr(e)
                )

                kayit_mesaji = (
                    "❌ Sindirim kaydı kaydedilemedi."
                )

    # --------------------------------------------------------
    # KAYITLARI GETİR
    # --------------------------------------------------------

    try:

        kayitlar = get_diarrhea_records()

    except Exception as e:

        print(
            "SİNDİRİM OKUMA HATASI:",
            repr(e)
        )

        kayitlar = []

    # --------------------------------------------------------
    # SAYFAYI GÖSTER
    # --------------------------------------------------------

    return render_template(
        "diarrhea.html",

        kayitlar=kayitlar,

        kayit_mesaji=kayit_mesaji
    )
    # ============================================================
# 7. BÖLÜM — İLAÇ TAKİBİ
# ============================================================

@app.route(
    "/medicine",
    methods=["GET", "POST"]
)
def medicine():

    kayit_mesaji = None

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        dose = request.form.get(
            "dose",
            ""
        ).strip()

        hour = request.form.get(
            "hour",
            ""
        ).strip()

        start_date = request.form.get(
            "start_date",
            ""
        ).strip()

        # ----------------------------------------------------
        # İLAÇ KAYDET
        # ----------------------------------------------------

        if name:

            try:

                save_medicine(
                    name,
                    dose,
                    hour,
                    start_date
                )

                kayit_mesaji = (
                    "✅ İlaç kaydın kaydedildi."
                )

            except Exception as e:

                print(
                    "İLAÇ KAYIT HATASI:",
                    repr(e)
                )

                kayit_mesaji = (
                    "❌ İlaç kaydı kaydedilemedi."
                )

    # --------------------------------------------------------
    # İLAÇLARI GETİR
    # --------------------------------------------------------

    try:

        kayitlar = get_medicines()

    except Exception as e:

        print(
            "İLAÇ OKUMA HATASI:",
            repr(e)
        )

        kayitlar = []

    # --------------------------------------------------------
    # SAYFAYI GÖSTER
    # --------------------------------------------------------

    return render_template(
        "medicine.html",

        kayitlar=kayitlar,

        kayit_mesaji=kayit_mesaji
    )


# ============================================================
# İLAÇ SİL
# ============================================================

@app.route(
    "/medicine/delete/<int:medicine_id>",
    methods=["POST"]
)
def medicine_delete(medicine_id):

    try:

        delete_medicine(
            medicine_id
        )

    except Exception as e:

        print(
            "İLAÇ SİLME HATASI:",
            repr(e)
        )

    return redirect(
        url_for("medicine")
    )
    # ============================================================
# 8. BÖLÜM — AYARLAR
# ============================================================

@app.route(
    "/settings",
    methods=["GET", "POST"]
)
def settings():

    kayit_mesaji = None

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        mode = request.form.get(
            "mode",
            "normal"
        ).strip()

        personality = request.form.get(
            "personality",
            "friendly"
        ).strip()

        # ----------------------------------------------------
        # AYARLARI KAYDET
        # ----------------------------------------------------

        try:

            save_settings(
                mode,
                personality
            )

            kayit_mesaji = (
                "✅ Ayarların kaydedildi."
            )

        except Exception as e:

            print(
                "AYAR KAYIT HATASI:",
                repr(e)
            )

            kayit_mesaji = (
                "❌ Ayarlar kaydedilemedi."
            )

    # --------------------------------------------------------
    # AYARLARI GETİR
    # --------------------------------------------------------

    try:

        settings_data = get_settings()

    except Exception as e:

        print(
            "AYAR OKUMA HATASI:",
            repr(e)
        )

        settings_data = {
            "mode": "normal",
            "personality": "friendly"
        }

    # --------------------------------------------------------
    # SAYFAYI GÖSTER
    # --------------------------------------------------------

    return render_template(
        "settings.html",

        settings=settings_data,

        kayit_mesaji=kayit_mesaji
    )
    # ============================================================
# 9. BÖLÜM — ARKADAŞ SOHBETİ ANA SAYFA
# ============================================================

@app.route(
    "/friends",
    methods=["GET", "POST"]
)
def friends():

    error = None
    room = None
    room_code = ""

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        ).strip()

        # ====================================================
        # YENİ ODA OLUŞTUR
        # ====================================================

        if action == "create":

            room_name = request.form.get(
                "room_name",
                "Arkadaş Sohbeti"
            ).strip()

            if not room_name:

                room_name = "Arkadaş Sohbeti"

            try:

                room_code = create_friend_room(
                    room_name
                )

                return redirect(
                    url_for(
                        "friend_room",
                        room_code=room_code
                    )
                )

            except Exception as e:

                print(
                    "ARKADAŞ ODASI OLUŞTURMA HATASI:",
                    repr(e)
                )

                error = (
                    "Sohbet odası oluşturulamadı."
                )

        # ====================================================
        # ODAYA KATIL
        # ====================================================

        elif action == "join":

            room_code = request.form.get(
                "room_code",
                ""
            ).strip().upper()

            if not room_code:

                error = (
                    "Lütfen sohbet kodunu gir."
                )

            else:

                try:

                    room = get_friend_room(
                        room_code
                    )

                    if not room:

                        error = (
                            "Bu sohbet koduna ait oda bulunamadı."
                        )

                    else:

                        return redirect(
                            url_for(
                                "friend_room",
                                room_code=room_code
                            )
                        )

                except Exception as e:

                    print(
                        "ARKADAŞ ODASI ARAMA HATASI:",
                        repr(e)
                    )

                    error = (
                        "Sohbet odası bulunurken "
                        "bir hata oluştu."
                    )

    # --------------------------------------------------------
    # ARKADAŞLAR SAYFASI
    # --------------------------------------------------------

    return render_template(
        "friends.html",

        room=room,

        room_code=room_code,

        error=error
    )
    # ============================================================
# 10. BÖLÜM — ARKADAŞ SOHBET ODASI
# ============================================================

@app.route(
    "/friends/<room_code>",
    methods=["GET", "POST"]
)
def friend_room(room_code):

    room_code = (
        room_code
        or ""
    ).strip().upper()

    # --------------------------------------------------------
    # ODAYI BUL
    # --------------------------------------------------------

    try:

        room = get_friend_room(
            room_code
        )

    except Exception as e:

        print(
            "ARKADAŞ ODASI OKUMA HATASI:",
            repr(e)
        )

        return redirect(
            url_for("friends")
        )

    if not room:

        return redirect(
            url_for("friends")
        )

    error = None

    # --------------------------------------------------------
    # MESAJ GÖNDER
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        if not username:

            username = "Misafir"

        if message:

            try:

                success = save_friend_message(
                    room_code,
                    username,
                    message
                )

                if not success:

                    error = (
                        "Mesaj gönderilemedi."
                    )

            except Exception as e:

                print(
                    "ARKADAŞ MESAJI KAYIT HATASI:",
                    repr(e)
                )

                error = (
                    "Mesaj gönderilirken "
                    "bir hata oluştu."
                )

    # --------------------------------------------------------
    # MESAJLARI GETİR
    # --------------------------------------------------------

    try:

        messages = get_friend_messages(
            room_code
        )

    except Exception as e:

        print(
            "ARKADAŞ MESAJLARI OKUMA HATASI:",
            repr(e)
        )

        messages = []

        error = (
            "Mesajlar yüklenemedi."
        )

    # --------------------------------------------------------
    # SOHBET ODASINI GÖSTER
    # --------------------------------------------------------

    return render_template(
        "friend_room.html",

        room=room,

        room_code=room_code,

        messages=messages,

        error=error
    )
