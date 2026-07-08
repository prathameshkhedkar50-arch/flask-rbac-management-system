from flask import Flask
from flask_cors import CORS
from .config import Config
from .db import db
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)
    register_routes(app)

    with app.app_context():
        from . import models
        from .seed import seed_data
        db.create_all()
        seed_data()

    return app