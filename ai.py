import os
from PIL import Image
from google import genai

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def ask_mavigpt(message, image_path=None):

    try:

        if image_path:

            image = Image.open(image_path)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image,
                    f"""
Sen MaviGPT'sin.

Kurallar:
- Her zaman Türkçe konuş.
- Samimi, nazik ve yardımsever ol.
- Fotoğraf varsa onu da değerlendir.
- Bilmediğin konuda tahmin yürütme.

Kullanıcı:
{message}
"""
                ]
            )

        else:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Sen MaviGPT'sin.

Kurallar:
- Her zaman Türkçe konuş.
- Samimi ve yardımsever ol.
- Kod, ders, günlük yaşam ve genel konularda yardımcı ol.
- Bilmediğin konuda uydurma bilgi verme.

Kullanıcı:
{message}
"""
            )

        return response.text

    except Exception as e:

        hata = str(e)

        if "429" in hata or "RESOURCE_EXHAUSTED" in hata:
            return (
                "🤖 MaviGPT şu anda biraz yoğun.\n\n"
                "Gemini kullanım kotası dolmuş olabilir.\n"
                "Biraz sonra tekrar deneyebilirsin. 💙"
            )

        return "Bir hata oluştu: " + hata
