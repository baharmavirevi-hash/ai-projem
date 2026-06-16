from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


    cevap = "Bir şey yaz 😊"

    if mesaj:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen yardımcı bir asistansın."},
                {"role": "user", "content": mesaj}
            ]
        )
        cevap = response.choices[0].message.content

    return f"""
    <html>
    <body style="font-family:Arial; background:#343541; color:white; text-align:center;">
        <h1>🤖 BaharGPT (Gerçek AI)</h1>

        <form>
            <input name="mesaj" style="padding:10px; width:60%;">
            <button>Gönder</button>
        </form>

        <div style="margin-top:20px;">
            <p><b>Sen:</b> {mesaj}</p>
            <p><b>AI:</b> {cevap}</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
