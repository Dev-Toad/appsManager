import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import datetime  # ¡Importamos datetime!

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


# ----------------------------------------------------
# 1. FUNCIÓN PARA FORMATEAR FECHAS (El Filtro)
# ----------------------------------------------------
def format_datetime(value, format="%d/%m/%Y %H:%M:%S"):
    """
    Formatea un objeto datetime a la cadena deseada.
    Se usa como un filtro de Jinja: {{ role.created_at | datetimeformat }}
    """
    if value is None:
        return ""
    # Si viene como cadena (por ejemplo, de algunos drivers de DB), la convierte
    if isinstance(value, str):
        try:
            # Asume formato ISO si es cadena
            value = datetime.fromisoformat(value)
        except ValueError:
            return value  # Retorna el valor original si falla la conversión

    return value.strftime(format)


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.dirname(os.path.dirname(base_dir))

    template_folder = os.path.join(project_root, "app", "views", "templates")
    static_folder = os.path.join(project_root, "app", "views", "static")

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from app import commands

    from app.routers import register_routes

    register_routes(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "app.login"
    commands.register_commands(app)

    # ----------------------------------------------------
    # 2. REGISTRO DEL FILTRO EN JINJA (Paso Crucial)
    # ----------------------------------------------------
    app.jinja_env.filters["datetimeformat"] = format_datetime

    return app
