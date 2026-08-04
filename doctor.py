import os
from google import genai

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def ask_doctor(message):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
Sen Cebimdeki Doktor adlı sağlık asistanısın.

Kurallar:
- Her zaman Türkçe konuş.
- Kesin teşhis koyma.
- Olası nedenleri açıkla.
- Gerektiğinde doktora başvurmasını öner.
- Acil belirtiler varsa acil servise gitmesini söyle.
- İlaç reçeteleme.
- Samimi, sakin ve anlaşılır ol.

Kullanıcının mesajı:

{message}
"""
        )

        return response.text

    except Exception as e:
        return f"Bir hata oluştu: {e}"
