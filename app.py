import logging

from flask import Flask, jsonify, redirect, request, url_for
from flask_login import LoginManager

from config import Config
from models import db, Admin
from routes import main

logging.basicConfig(level=logging.INFO)

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "main.index"


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    return redirect(url_for("main.index"))


app.register_blueprint(main)

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)