from flask import Flask
from routes import register_routes
from database import init_db
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# uploads klasörü yoksa oluştur
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Veritabanını oluştur
init_db()

# Route'ları yükle
register_routes(app)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
