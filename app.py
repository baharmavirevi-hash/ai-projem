import os

from flask import Flask

from database import init_db
from routes import register_routes


app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

init_db()
register_routes(app)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )

