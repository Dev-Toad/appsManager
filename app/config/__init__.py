import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import datetime

from app.context_processors import inject_user_data


load_dotenv()


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


class Config:
    """Configuración base para Flask, cargada desde variables de entorno."""

    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-de-desarrollo")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "versions")
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024
    ALLOWED_EXTENSIONS = {
        "deb",
        "rpm",
        "exe",
        "msi",
        "dmg",
        "pkg",
        "zip",
        "tar",
        "gz",
        "tar.gz",
        "yml",
        "yaml",
    }

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


def format_datetime(value, format="%d/%m/%Y %H:%M:%S"):
    """
    Formatea un objeto datetime a la cadena deseada.
    Se usa como un filtro de Jinja: {{ role.created_at | datetimeformat }}
    """
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:

            return value

    return value.strftime(format)


def create_app(config_object=Config):
    """Crea y configura la instancia de la aplicación Flask."""

    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.dirname(os.path.dirname(base_dir))

    template_folder = os.path.join(project_root, "app", "views", "templates")
    static_folder = os.path.join(project_root, "app", "views", "static")

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "app.login"

    from app import commands
    from app.routers import register_routes

    register_routes(app)
    commands.register_commands(app)
    app.context_processor(inject_user_data)

    app.jinja_env.filters["datetimeformat"] = format_datetime

    return app
