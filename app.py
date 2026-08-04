from flask import Flask
from routes import register_routes
import os

app = Flask(__name__)

# Fotoğraf yükleme klasörü
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Klasör yoksa oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tüm sayfaları yükle
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
