from flask import render_template, request
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
    get_medicines
)


# ============================================================
# GEMINI
# ============================================================

def ask_mavigpt(message, image_path=None):

    try:

        if not message:
            message = "Merhaba!"

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            return (
                "MaviGPT şu anda çalışıyor fakat "
                "GEMINI_API_KEY ayarı bulunamadı."
            )

        client = genai.Client(
            api_key=api_key
        )

        # ----------------------------------------------------
        # FOTOĞRAFLI İSTEK
        # ----------------------------------------------------

        if image_path:

            try:

                image = Image.open(image_path)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        image,
                        message
                    ]
                )

            except Exception as e:

                print(
                    "FOTOĞRAF ANALİZ HATASI:",
                    repr(e)
                )

                return (
                    "Fotoğrafı şu anda inceleyemedim. "
                    "Lütfen tekrar dene."
                )

        # ----------------------------------------------------
        # NORMAL İSTEK
        # ----------------------------------------------------

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message
            )

        if response and response.text:

            return response.text

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

    try:

        if "foto" not in request.files:
            return None, None

        file = request.files["foto"]

        if not file:
            return None, None

        if file.filename == "":
            return None, None

        original_name = secure_filename(
            file.filename
        )

        if not original_name:
            return None, None

        # ----------------------------------------------------
        # Aynı isimli fotoğrafların üzerine yazılmasını önle.
        # ----------------------------------------------------

        extension = ""

        if "." in original_name:

            extension = (
                "." +
                original_name.rsplit(".", 1)[1].lower()
            )

        filename = (
            uuid.uuid4().hex +
            extension
        )

        # ----------------------------------------------------
        # UPLOAD_FOLDER yoksa static/uploads kullan.
        # ----------------------------------------------------

        upload_folder = app.config.get(
            "UPLOAD_FOLDER"
        )

        if not upload_folder:

            upload_folder = os.path.join(
                app.static_folder,
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

        file.save(path)

        return path, filename

    except Exception as e:

        print(
            "FOTOĞRAF YÜKLEME HATASI:",
            repr(e)
        )

        return None, None


# ============================================================
# FOTOĞRAF URL
# ============================================================

def photo_url(app, filename):

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

        print("================================")
        print("MAVIGPT HOME CALISTI")
        print("METHOD:", request.method)
        print("================================")

        mesaj = ""
        cevap = ""
        filename = None

        # ----------------------------------------------------
        # SOHBETLERİ OKU
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
                "GELEN MESAJ:",
                mesaj
            )

            foto, filename = upload_photo(
                app
            )

            print(
                "FOTOGRAF:",
                filename
            )

            # ------------------------------------------------
            # Mesaj veya fotoğraf yoksa cevap üretme.
            # ------------------------------------------------

            if mesaj or foto:

                if mesaj:

                    ai_mesaj = mesaj

                else:

                    ai_mesaj = (
                        "Bu fotoğrafı incele. "
                        "Gördüğün şey hakkında "
                        "genel, güvenli ve anlaşılır "
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

                # --------------------------------------------
                # SOHBETİ DATABASE'E KAYDET
                # --------------------------------------------

                try:

                    save_chat(
                        "normal",
                        mesaj if mesaj else "📷 Fotoğraf",
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

        return render_template(
            "mavigpt.html",

            mesaj=mesaj,

            cevap=cevap,

            foto_url=photo_url(
                app,
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

        mesaj = ""
        cevap = ""
        filename = None
        kayit_mesaji = None

        if request.method == "POST":

            # ------------------------------------------------
            # Mesaj
            # ------------------------------------------------

            mesaj = request.form.get(
                "mesaj",
                ""
            ).strip()

            # ------------------------------------------------
            # Ayrı sağlık kayıt alanları
            # ------------------------------------------------

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
            # FOTOĞRAF
            # ------------------------------------------------

            foto, filename = upload_photo(
                app
            )

            # ------------------------------------------------
            # Sağlık formundan kayıt geldiyse kaydet.
            # ------------------------------------------------

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
                        "Kayıt sırasında bir sorun oluştu."
                    )

            # ------------------------------------------------
            # Mesaj veya fotoğraf varsa AI'ya gönder.
            # ------------------------------------------------

            if mesaj or foto:

                if mesaj:

                    ai_mesaj = mesaj

                else:

                    ai_mesaj = (
                        "Bu sağlık fotoğrafını "
                        "incele ve gördüğün şey hakkında "
                        "genel, güvenli ve anlaşılır "
                        "bilgi ver. Kesin teşhis koyma."
                    )

                cevap = ask_mavigpt(
                    ai_mesaj,
                    foto
                )

                # ------------------------------------------------
                # Doktor konuşmasını da kaydet.
                # ------------------------------------------------

                try:

                    save_chat(
                        "doctor",
                        mesaj if mesaj else "📷 Sağlık fotoğrafı",
                        cevap
                    )

                except Exception as e:

                    print(
                        "DOKTOR SOHBET KAYIT HATASI:",
                        repr(e)
                    )

        # ----------------------------------------------------
        # Sağlık kayıtlarını tekrar oku.
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

            foto_url=photo_url(
                app,
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

            # ------------------------------------------------
            # Başlangıç tarihi varsa kayıt oluştur.
            # ------------------------------------------------

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
                        "Regl kaydı sırasında bir sorun oluştu."
                    )

        # ----------------------------------------------------
        # Kayıtları yeniden oku.
        # ----------------------------------------------------

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
    # SİNDİRİM TAKİBİ
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

            count = request.form.get(
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
                        "Sindirim kaydı sırasında bir sorun oluştu."
                    )

        # ----------------------------------------------------
        # Kayıtları yeniden oku.
        # ----------------------------------------------------

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
    # İLAÇLAR
    # ========================================================

    @app.route(
        "/medicine",
        methods=["GET", "POST"]
    )
    def medicine():

        kayit_mesaji = None

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
                        "İlaç kaydı sırasında bir sorun oluştu."
                    )

        # ----------------------------------------------------
        # İlaçları yeniden oku.
        # ----------------------------------------------------

        try:

            ilaclar = get_medicines()

        except Exception as e:

            print(
                "İLAÇLAR OKUNAMADI:",
                repr(e)
            )

            ilaclar = []

        return render_template(
            "medicine.html",

            ilaclar=ilaclar,

            kayit_mesaji=kayit_mesaji
        )
        
