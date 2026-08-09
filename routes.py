from flask import (
    render_template,
    request,
    redirect,
    url_for
)

import os
import uuid

from werkzeug.utils import secure_filename
from PIL import Image
from google import genai

from database import (
    save_chat,
    get_chats,

    save_health_record,
    get_health_records,

    save_period_record,
    get_period_records,

    save_diarrhea_record,
    get_diarrhea_records,

    save_medicine,
    get_medicines,
    delete_medicine
)


# ============================================================
# GEMINI / MAVIGPT
# ============================================================

def ask_mavigpt(
    message,
    image_path=None
):

    try:

        if not message:

            message = "Merhaba!"

        api_key = os.environ.get(
            "GEMINI_API_KEY"
        )

        if not api_key:

            return (
                "MaviGPT şu anda çalışıyor fakat "
                "GEMINI_API_KEY ayarı bulunamadı."
            )

        client = genai.Client(
            api_key=api_key
        )

        # ----------------------------------------------------
        # FOTOĞRAFLI MESAJ
        # ----------------------------------------------------

        if image_path:

            try:

                image = Image.open(
                    image_path
                )

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        image,
                        message
                    ]
                )

            except Exception as e:

                print(
                    "FOTOĞRAF OKUMA HATASI:",
                    repr(e)
                )

                return (
                    "Fotoğrafı şu anda okuyamadım. "
                    "Lütfen tekrar göndermeyi dene."
                )

        # ----------------------------------------------------
        # NORMAL MESAJ
        # ----------------------------------------------------

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message
            )

        if response and response.text:

            return response.text.strip()

        return (
            "Şu anda cevap oluşturamadım. "
            "Lütfen tekrar dene."
        )

    except Exception as e:

        print(
            "GEMINI HATASI:",
            repr(e)
        )

        return (
            "MaviGPT cevap oluştururken bir sorun yaşadı. "
            "Biraz sonra tekrar deneyebilirsin."
        )


# ============================================================
# FOTOĞRAF YÜKLEME
# ============================================================

def upload_photo(app):

    if "foto" not in request.files:

        return None, None

    file = request.files["foto"]

    if not file:

        return None, None

    if not file.filename:

        return None, None

    original_name = secure_filename(
        file.filename
    )

    if not original_name:

        return None, None

    extension = os.path.splitext(
        original_name
    )[1].lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif"
    }

    if extension not in allowed_extensions:

        print(
            "DESTEKLENMEYEN FOTOĞRAF:",
            extension
        )

        return None, None

    filename = (
        uuid.uuid4().hex +
        extension
    )

    upload_folder = app.config.get(
        "UPLOAD_FOLDER"
    )

    if not upload_folder:

        upload_folder = os.path.join(
            app.root_path,
            "static",
            "uploads"
        )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    path = os.path.join(
        upload_folder,
        filename
    )

    try:

        file.save(path)

        if not os.path.exists(path):

            print(
                "FOTOĞRAF OLUŞMADI:",
                path
            )

            return None, None

        return path, filename

    except Exception as e:

        print(
            "FOTOĞRAF KAYDETME HATASI:",
            repr(e)
        )

        return None, None


# ============================================================
# FOTOĞRAF URL
# ============================================================

def get_photo_url(filename):

    if not filename:

        return None

    return (
        "/static/uploads/" +
        filename
    )


# ============================================================
# ROUTES
# ============================================================

def register_routes(app):


    # ========================================================
    # MAVIGPT
    # ========================================================

    @app.route(
        "/",
        methods=["GET", "POST"]
    )
    def home():

        mesaj = ""
        cevap = ""
        filename = None

        # ----------------------------------------------------
        # SOHBET GEÇMİŞİ
        # ----------------------------------------------------

        try:

            sohbetler = get_chats(
                "normal"
            )

        except Exception as e:

            print(
                "SOHBETLER OKUNAMADI:",
                repr(e)
            )

            sohbetler = []

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

            print(
                "================================"
            )

            print(
                "MAVIGPT MESAJ:",
                mesaj
            )

            foto, filename = upload_photo(
                app
            )

            print(
                "MAVIGPT FOTO:",
                filename
            )

            if mesaj or foto:

                if mesaj:

                    ai_mesaj = mesaj

                else:

                    ai_mesaj = (
                        "Bu fotoğrafı incele. "
                        "Gördüğün şey hakkında "
                        "genel, anlaşılır ve güvenli "
                        "bilgi ver."
                    )

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto
                )

                print(
                    "MAVIGPT CEVAP:",
                    cevap
                )

                # ------------------------------------------------
                # SOHBETİ KAYDET
                # ------------------------------------------------

                try:

                    save_chat(
                        "normal",
                        mesaj if mesaj else "Fotoğraf",
                        cevap
                    )

                    sohbetler = get_chats(
                        "normal"
                    )

                except Exception as e:

                    print(
                        "SOHBET KAYIT HATASI:",
                        repr(e)
                    )

            print(
                "================================"
            )

        return render_template(
            "mavigpt.html",
            mesaj=mesaj,
            cevap=cevap,
            foto_url=get_photo_url(
                filename
            ),
            sohbetler=sohbetler
        )


    # ========================================================
    # CEBİMDEKİ DOKTOR
    # ========================================================

    @app.route(
        "/doctor",
        methods=["GET", "POST"]
    )
    def doctor():

        mesaj = None
        cevap = None
        filename = None
        kayit_mesaji = None

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

            # ------------------------------------------------
            # SAĞLIK KAYDI
            # ------------------------------------------------

            if (
                symptom
                or medicine
                or note
            ):

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

            # ------------------------------------------------
            # FOTOĞRAF
            # ------------------------------------------------

            foto, filename = upload_photo(
                app
            )

            # ------------------------------------------------
            # MAVIGPT
            # ------------------------------------------------

            if mesaj or foto:

                if mesaj:

                    ai_mesaj = mesaj

                else:

                    ai_mesaj = (
                        "Bu sağlık fotoğrafı hakkında "
                        "genel ve anlaşılır bilgi ver. "
                        "Kesin tanı koyma."
                    )

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto
                )

        # ----------------------------------------------------
        # KAYITLARI GETİR
        # ----------------------------------------------------

        try:

            kayitlar = get_health_records()

        except Exception as e:

            print(
                "SAĞLIK KAYITLARI OKUNAMADI:",
                repr(e)
            )

            kayitlar = []

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


    # ========================================================
    # REGL TAKİBİ
    # ========================================================

    @app.route(
        "/period",
        methods=["GET", "POST"]
    )
    def period():

        kayit_mesaji = None

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

        try:

            kayitlar = get_period_records()

        except Exception as e:

            print(
                "REGL KAYITLARI OKUNAMADI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "period.html",
            kayitlar=kayitlar,
            kayit_mesaji=kayit_mesaji
        )


    # ========================================================
    # SİNDİRİM / İSHAL TAKİBİ
    # ========================================================

    @app.route(
        "/diarrhea",
        methods=["GET", "POST"]
    )
    def diarrhea():

        kayit_mesaji = None

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

            count = 0

            if count_raw:

                try:

                    count = int(
                        count_raw
                    )

                    if count < 0:

                        count = 0

                except (
                    ValueError,
                    TypeError
                ):

                    count = 0

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

        try:

            kayitlar = get_diarrhea_records()

        except Exception as e:

            print(
                "SİNDİRİM KAYITLARI OKUNAMADI:",
                repr(e)
            )

            kayitlar = []

        return render_template(
            "diarrhea.html",
            kayitlar=kayitlar,
            kayit_mesaji=kayit_mesaji
        )


        # ========================================================
# İLAÇLARIM
# ========================================================

@app.route("/medicine", methods=["GET", "POST"])
def medicine():

    kayit_mesaji = None

    # ----------------------------------------------------
    # İLAÇ EKLE
    # ----------------------------------------------------

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        dose = request.form.get("dose", "").strip()
        hour = request.form.get("hour", "").strip()
        start_date = request.form.get("start_date", "").strip()

        if name:

            try:

                save_medicine(
                    name,
                    dose,
                    hour,
                    start_date
                )

                kayit_mesaji = "İlaç başarıyla kaydedildi."

            except Exception as e:

                print("İLAÇ KAYIT HATASI:", repr(e))

                kayit_mesaji = "İlaç kaydedilemedi."

    # ----------------------------------------------------
    # İLAÇLARI GETİR
    # ----------------------------------------------------

    try:

        kayitlar = get_medicines()

        print("================================")
        print("İLAÇLAR:")
        print("SAYI:", len(kayitlar))

        for ilac in kayitlar:
            print(dict(ilac))

        print("================================")

    except Exception as e:

        print("İLAÇLAR OKUNAMADI:", repr(e))

        kayitlar = []

        kayit_mesaji = "İlaç kayıtları okunamadı."

    return render_template(
        "medicine.html",
        kayitlar=kayitlar,
        kayit_mesaji=kayit_mesaji
    )


# ========================================================
# İLAÇ SİL
# ========================================================

@app.route(
    "/medicine/delete/<int:medicine_id>",
    methods=["POST"]
)
def medicine_delete(medicine_id):

    try:

        delete_medicine(medicine_id)

    except Exception as e:

        print(
            "İLAÇ SİLME HATASI:",
            repr(e)
        )

    return redirect(
        url_for("medicine")
    )


    

        # ----------------------------------------------------
        # ID YOKSA
        # ----------------------------------------------------

        if not medicine_id:

            print(
                "İLAÇ SİLME: ID YOK"
            )

            return redirect(
                url_for("medicine")
            )

        # ----------------------------------------------------
        # ID SAYIYA ÇEVİR
        # ----------------------------------------------------

        try:

            medicine_id = int(
                medicine_id
            )

        except (
            ValueError,
            TypeError
        ):

            print(
                "İLAÇ SİLME: GEÇERSİZ ID:",
                medicine_id
            )

            return redirect(
                url_for("medicine")
            )

        # ----------------------------------------------------
        # SİL
        # ----------------------------------------------------

        try:

            deleted = delete_medicine(
                medicine_id
            )

            if deleted:

                print(
                    "İLAÇ BAŞARIYLA SİLİNDİ:",
                    medicine_id
                )

            else:

                print(
                    "İLAÇ BULUNAMADI:",
                    medicine_id
                )

        except Exception as e:

            print(
                "İLAÇ SİLME ROUTE HATASI:",
                repr(e)
            )

        # ----------------------------------------------------
        # İLAÇLAR SAYFASINA DÖN
        # ----------------------------------------------------

        return redirect(
            url_for("medicine")
        )


    # ========================================================
    # AYARLAR
    # ========================================================

    @app.route(
        "/settings",
        methods=["GET"]
    )
    def settings():

        return redirect(
            url_for("doctor")
            )
