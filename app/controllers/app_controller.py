from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Application, User, Role, Version
from app.config import db 
from datetime import datetime

# app_bp = Blueprint('app', __name__)


def dashboard():
    apps = Application.query.all()
    return render_template('dashboard/applications.html', apps=apps)

def new_app():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']
        stack = request.form['stack']
        framework = request.form['framework']
        repositorio_url = request.form['repositorio_url']
        estado = request.form.get('estado', 'Activa')
        fecha_creacion = request.form.get('fecha_creacion')
        owner_id = request.form['owner_id']
        tipo_entorno = request.form.get('tipo_entorno', 'servidor')
        version_docker = request.form.get('version_docker') if tipo_entorno == 'docker' else None

        owner = User.query.join(Role).filter(User.id == owner_id, Role.nombre == 'Desarrollador').first()
        if not owner:
            flash('Usuario dueño no válido o no es Desarrollador')
            return redirect(url_for('app.new_app'))

        app = Application(
            nombre=nombre,
            descripcion=descripcion,
            tipo=tipo,
            stack=stack,
            framework=framework,
            repositorio_url=repositorio_url,
            estado=estado,
            fecha_creacion=fecha_creacion,
            owner_id=owner_id,
            tipo_entorno=tipo_entorno,
            version_docker=version_docker
        )
        db.session.add(app)
        db.session.commit()
        flash('Aplicación creada con éxito')
        return redirect(url_for('app.dashboard'))

    developers = User.query.join(Role).filter(Role.nombre == 'Desarrollador').all()
    return render_template('dashboard/new_app.html', users=developers)


def edit_app(app_id):
    app = Application.query.get_or_404(app_id)
    if app.owner_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        app.nombre = request.form['nombre']
        app.descripcion = request.form['descripcion']
        app.tipo = request.form['tipo']
        app.stack = request.form['stack']
        app.framework = request.form['framework']
        app.repositorio_url = request.form['repositorio_url']
        app.estado = request.form.get('estado', 'Activa')
        app.fecha_creacion = request.form.get('fecha_creacion')
        app.owner_id = request.form['owner_id']

        owner = User.query.join(Role).filter(User.id == app.owner_id, Role.nombre == 'Desarrollador').first()
        if not owner:
            flash('Usuario dueño no válido o no es Desarrollador')
            return redirect(url_for('app.edit_app', app_id=app_id))

        db.session.commit()
        flash('Aplicación actualizada con éxito')
        return redirect(url_for('app.dashboard'))

    developers = User.query.join(Role).filter(Role.nombre == 'Desarrollador').all()
    return render_template('dashboard/edit_app.html', app=app, users=developers)

def delete_app(app_id):
    app = Application.query.get_or_404(app_id)
    if app.owner_id != current_user.id:
        abort(403)

    db.session.delete(app)
    db.session.commit()
    flash('Aplicación eliminada')
    return redirect(url_for('app.dashboard'))


def view_app(app_id):
    app = Application.query.get_or_404(app_id)
    versions = Version.query.filter_by(aplicacion_id=app_id).order_by(Version.numero_version.desc()).all()
    return render_template('dashboard/view_app.html', app=app, versions=versions)