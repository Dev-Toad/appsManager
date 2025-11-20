from app.controllers import (
    auth_controller,
    app_controller,
    version_controller,
    role_controller,
    user_controller,
    dashboard_controller,
)
from flask import Blueprint
from flask_login import login_required


def register_routes(app):
    app_bp = Blueprint("app", __name__)
    user_bp = Blueprint("user", __name__)
    rol_bp = Blueprint("rol", __name__)

    # Version Route auth_controller
    @app_bp.route("/")
    def index():
        return auth_controller.index()

    @app_bp.route("/login", methods=["GET", "POST"])
    def login():
        return auth_controller.login()

    @app_bp.route("/logout")
    @login_required
    def logout():
        return auth_controller.logout()

    # Dashboard Route dashboard_controller
    @app_bp.route("/dashboard")
    @login_required
    def dashboard():
        return dashboard_controller.dashboard()

    # App Route app_controller

    @app_bp.route("/app")
    @login_required
    def app_list():
        return app_controller.app_list()

    @app_bp.route("/new/app", methods=["GET", "POST"])
    @login_required
    def new_app():
        return app_controller.new_app()

    @app_bp.route("/app/<int:app_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_app(app_id):
        return app_controller.edit_app(app_id)

    @app_bp.route("/app/<int:app_id>/delete", methods=["POST"])
    @login_required
    def delete_app(app_id):
        return app_controller.delete_app(app_id)

    @app_bp.route("/app/<int:app_id>")
    @login_required
    def view_app(app_id):
        return app_controller.view_app(app_id)

    # Version Route version_controller
    @app_bp.route("/app/<int:app_id>/version/new", methods=["GET", "POST"])
    @login_required
    def new_version(app_id):
        return version_controller.new_version(app_id)

    @app_bp.route("/version/<int:version_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_version(version_id):
        return version_controller.edit_version(version_id)

    @app_bp.route("/version/<int:version_id>/delete", methods=["POST"])
    @login_required
    def delete_version(version_id):
        return version_controller.delete_version(version_id)

    # Version Route role_controller
    @rol_bp.route("/roles")
    @login_required
    def list_roles():
        return role_controller.list_roles()

    @rol_bp.route("/roles/new", methods=["GET", "POST"])
    @login_required
    def new_role():
        return role_controller.new_role()

    @rol_bp.route("/roles/<int:role_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_role(role_id):
        return role_controller.edit_role(role_id)

    @rol_bp.route("/roles/<int:role_id>")
    @login_required
    def view_role(role_id):
        return role_controller.view_role(role_id)

    @rol_bp.route("/roles/<int:role_id>/toggle_status")
    @login_required
    def toggle_role_status(role_id):
        return role_controller.toggle_role_status(role_id)

    # Version Route user_controller
    @user_bp.route("/users")
    @login_required
    def list_users():
        return user_controller.list_users()

    @user_bp.route("/users/<int:user_id>")
    @login_required
    def view_user(user_id):
        return user_controller.view_user(user_id)

    @user_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_user(user_id):
        return user_controller.edit_user(user_id)

    @user_bp.route("/users/<int:user_id>/toggle_status")
    @login_required
    def toggle_user_status(user_id):
        return user_controller.toggle_user_status(user_id)

    @user_bp.route("/users/new", methods=["GET", "POST"])
    @login_required
    def new_user():
        return user_controller.new_user()

    app.register_blueprint(app_bp)
    app.register_blueprint(rol_bp)
    app.register_blueprint(user_bp)
