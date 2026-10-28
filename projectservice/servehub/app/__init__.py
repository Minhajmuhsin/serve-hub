from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "temporary-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///servehub.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from .routes.main import main
    from .routes.auth import auth
    from .routes.admin import admin
    from .routes.services import services

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(services)

    from . import models

    with app.app_context():
        db.create_all()

    return app