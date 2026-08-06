from flask import Flask
from routes import register_routes
from database import init_db
import os


app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = "static/uploads"


os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


init_db()


register_routes(app)



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT",5000)),
        debug=False
    )
