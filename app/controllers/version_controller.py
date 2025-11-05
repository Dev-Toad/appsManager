from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Version, Application, User, Role
from app.config import db 
from datetime import datetime

version_bp = Blueprint('version', __name__)

@version_bp.route('/app/<int:app_id>/version/new', methods=['GET', 'POST'])
@login_required
def new_version(app_id):
    app = Application.query.get_or_404(app_id)

    if request.method == 'POST':
        numero_version = request.form['numero_version'] 
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        documentacion_url = request.form['documentacion_url']
        gestor_bd = request.form['gestor_bd']
        version_gestor_bd = request.form['version_gestor_bd']
        dependencias = request.form['dependencias']
        fecha_inicio_soporte = request.form.get('fecha_inicio_soporte')
        fecha_fin_soporte = request.form.get('fecha_fin_soporte')
        owner_id = request.form['owner_id']

        # Validar que el owner sea desarrollador
        owner = User.query.join(Role).filter(User.id == owner_id, Role.nombre == 'Desarrollador').first()
        if not owner:
            flash('Usuario dueño no válido o no es Desarrollador')
            return redirect(url_for('version.new_version', app_id=app_id))

        version = Version(
            aplicacion_id=app_id,
            numero_version=numero_version,
            titulo=titulo,
            descripcion=descripcion,
            documentacion_url=documentacion_url,
            gestor_bd=gestor_bd,
            version_gestor_bd=version_gestor_bd,
            dependencias=dependencias,
            fecha_inicio_soporte=fecha_inicio_soporte,
            fecha_fin_soporte=fecha_fin_soporte,
            owner_id=owner_id
        )
        db.session.add(version)
        db.session.commit()
        flash('Versión creada con éxito')
        return redirect(url_for('app.view_app', app_id=app_id))

    # ✅ Obtener SOLO usuarios con rol "Desarrollador"
    developers = User.query.join(Role).filter(Role.nombre == 'Desarrollador').all()
    return render_template('dashboard/new_version.html', app=app, users=developers)

@version_bp.route('/version/<int:version_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_version(version_id):
    version = Version.query.get_or_404(version_id)
    if version.release_owner.id != current_user.id:
        abort(403)

    if request.method == 'POST':
        version.titulo = request.form['titulo']
        version.descripcion = request.form['descripcion']
        version.documentacion_url = request.form['documentacion_url']
        version.gestor_bd = request.form['gestor_bd']
        version.version_gestor_bd = request.form['version_gestor_bd']
        version.dependencias = request.form['dependencias']
        version.fecha_inicio_soporte = request.form.get('fecha_inicio_soporte')
        version.fecha_fin_soporte = request.form.get('fecha_fin_soporte')
        version.owner_id = request.form['owner_id']

        # Validar nuevo owner
        owner = User.query.join(Role).filter(User.id == version.owner_id, Role.nombre == 'Desarrollador').first()
        if not owner:
            flash('Usuario dueño no válido o no es Desarrollador')
            return redirect(url_for('version.edit_version', version_id=version_id))

        db.session.commit()
        flash('Versión actualizada')
        return redirect(url_for('app.view_app', app_id=version.aplicacion_id))

    developers = User.query.join(Role).filter(Role.nombre == 'Desarrollador').all()
    return render_template('dashboard/edit_version.html', version=version, users=developers)

@version_bp.route('/version/<int:version_id>/delete', methods=['POST'])
@login_required
def delete_version(version_id):
    version = Version.query.get_or_404(version_id)
    if version.release_owner.id != current_user.id:
        abort(403)

    app_id = version.aplicacion_id
    db.session.delete(version)
    db.session.commit()
    flash('Versión eliminada')
    return redirect(url_for('app.view_app', app_id=app_id))