import os
from google import genai

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def ask_doctor(mesaj):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
Sen Cebimdeki Doktor adlı sağlık asistanısın.

Kurallar:

- Her zaman Türkçe konuş.
- Doktor gibi kesin teşhis koyma.
- Hastalık varmış gibi davranma.
- Olası nedenleri açıkla.
- Gerektiğinde doktora başvurmasını öner.
- Acil belirtiler varsa acil servise gitmesini söyle.
- İlaç reçeteleme.
- Samimi ve anlaşılır konuş.

Kullanıcı:

{mesaj}
"""
        )

        return response.text

    except Exception as e:
        return f"Hata: {e}"
