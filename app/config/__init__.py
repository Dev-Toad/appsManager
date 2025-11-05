import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Cargar variables de entorno
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    # Obtener la ruta absoluta del directorio actual (donde está este archivo)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    # Subir dos niveles para llegar a la raíz del proyecto
    project_root = os.path.dirname(os.path.dirname(base_dir))
    
    # Configurar rutas de templates y static
    template_folder = os.path.join(project_root, 'app', 'views', 'templates')
    static_folder = os.path.join(project_root, 'app', 'views', 'static')
    
    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.controllers.auth_controller import auth_bp
    from app.controllers.app_controller import app_bp
    from app.controllers.version_controller import version_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(app_bp)
    app.register_blueprint(version_bp)

    return app