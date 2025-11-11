from app.controllers import auth_controller, app_controller, version_controller
from flask import Blueprint
from flask_login import login_required, current_user


def register_routes(app):
    app_bp = Blueprint('app', __name__)
    
    # Version Route auth_controller
    @app_bp.route('/')
    def index():
        return auth_controller.index() 
    
    @app_bp.route('/login', methods=['GET', 'POST'])
    def login():
        return auth_controller.login()  
    

    @app_bp.route('/logout')
    @login_required
    def logout():
        return auth_controller.logout()
    
    
    # Version Route app_controller
    @app_bp.route('/dashboard')
    @login_required
    def dashboard():
        return app_controller.dashboard()
    
    @app_bp.route('/new/app')
    @login_required
    def new_app():
        return app_controller.new_app()
    
    @app_bp.route('/app/<int:app_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_app(app_id):
        return app_controller.edit_app(app_id)
    
    @app_bp.route('/app/<int:app_id>/delete', methods=['POST'])
    @login_required
    def delete_app(app_id):
        return app_controller.delete_app(app_id)
    
    @app_bp.route('/app/<int:app_id>')
    @login_required
    def view_app(app_id):
        return app_controller.view_app(app_id)
    

    # Version Route version_controller
    @app_bp.route('/app/<int:app_id>/version/new', methods=['GET', 'POST'])
    @login_required
    def new_version(app_id):
        return version_controller.new_version(app_id)

    @app_bp.route('/version/<int:version_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_version(version_id):
        return version_controller.edit_version(version_id)
    
    @app_bp.route('/version/<int:version_id>/delete', methods=['POST'])
    @login_required
    def delete_version(version_id):
        return version_controller.delete_version(version_id)
    



    app.register_blueprint(app_bp)  


