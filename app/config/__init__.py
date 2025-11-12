import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.dirname(os.path.dirname(base_dir))

    template_folder = os.path.join(project_root, "app", "views", "templates")
    static_folder = os.path.join(project_root, "app", "views", "static")

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from app.routers import register_routes

    register_routes(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # The login route is registered under the 'app' blueprint as 'app.login'
    login_manager.login_view = "app.login"

    return app
