from flask import Flask
from routes import register_routes
from database import init_db
import os


# ============================================================
# FLASK UYGULAMASI
# ============================================================

app = Flask(__name__)


# ============================================================
# UPLOAD KLASÖRÜ
# ============================================================

app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


# ============================================================
# DATABASE
# ============================================================

init_db()


# ============================================================
# ROUTES
# ============================================================

register_routes(app)


# ============================================================
# LOCAL / RAILWAY ÇALIŞTIRMA
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
