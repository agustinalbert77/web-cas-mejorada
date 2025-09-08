from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from .config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(
        __name__,
        instance_relative_config=False,
        template_folder="../templates",    # <- ahora Flask sabrá dónde buscar
        static_folder="../static"          # <- y dónde están tus archivos estáticos
    )
    app.config.from_object(Config())

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"

    from .routes.public import public_bp
    from .routes.auth import auth_bp
    from .routes.intranet import intranet_bp
    from .routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(intranet_bp, url_prefix="/intranet")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        from . import models
        db.create_all()

        from .models import User
        if not User.query.filter_by(email="admin@dsls.cl").first():
            admin = User(name="Administrador", email="admin@dsls.cl", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app

