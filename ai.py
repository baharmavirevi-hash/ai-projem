import os
from google import genai

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


def ask_mavigpt(message):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
Sen MaviGPT'sin.

Kurallar:
- Her zaman Türkçe konuş.
- Samimi, yardımsever ve anlaşılır ol.
- Kod yazabilirsin.
- Derslerde yardımcı olabilirsin.
- Sohbet edebilirsin.
- Gerektiğinde maddeler halinde açıklama yap.

Kullanıcının mesajı:

{message}
"""
        )

        return response.text

    except Exception as e:
        return f"Bir hata oluştu: {e}"
