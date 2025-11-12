from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.models import Application, User, Role, Version
from app.config import db
from datetime import datetime


def dashboard():
    apps = Application.query.all()
    return render_template("dashboard/applications.html", apps=apps)


def new_app():
    if request.method == "POST":
        # Campos requeridos
        nombre = request.form.get("nombre")
        if not nombre:
            flash("El campo 'nombre' es requerido")
            return redirect(url_for("app.new_app"))

        descripcion = request.form.get("descripcion")
        tipo = request.form.get("tipo")
        stack = request.form.get("stack")
        framework = request.form.get("framework")
        repositorio_url = request.form.get("repositorio_url")
        estado = request.form.get("estado", "Activa")
        fecha_creacion_raw = request.form.get("fecha_creacion")
        owner_id_raw = request.form.get("owner_id")
        tipo_entorno = request.form.get("tipo_entorno", "servidor")
        version_docker = (
            request.form.get("version_docker") if tipo_entorno == "docker" else None
        )

        # Normalizar owner_id a entero
        try:
            owner_id = int(owner_id_raw)
        except (TypeError, ValueError):
            flash("Owner inválido")
            return redirect(url_for("app.new_app"))

        # Parsear fecha si viene
        fecha_creacion = None
        if fecha_creacion_raw:
            try:
                # HTML date inputs typically send YYYY-MM-DD
                fecha_creacion = datetime.fromisoformat(fecha_creacion_raw).date()
            except ValueError:
                try:
                    fecha_creacion = datetime.strptime(
                        fecha_creacion_raw, "%Y-%m-%d"
                    ).date()
                except Exception:
                    flash("Formato de fecha inválido")
                    return redirect(url_for("app.new_app"))

        owner = (
            User.query.join(Role)
            .filter(User.id == owner_id, Role.nombre == "Desarrollador")
            .first()
        )
        if not owner:
            flash("Usuario dueño no válido o no es Desarrollador")
            return redirect(url_for("app.new_app"))

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
            version_docker=version_docker,
        )
        db.session.add(app)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar la aplicación: {e}")
            return redirect(url_for("app.new_app"))

        flash("Aplicación creada con éxito")
        return redirect(url_for("app.dashboard"))

    developers = User.query.join(Role).filter(Role.nombre == "Desarrollador").all()
    return render_template("dashboard/new_app.html", users=developers)


def edit_app(app_id):
    app = db.session.get(Application, app_id)
    if not app:
        abort(404)
    if app.owner_id != current_user.id:
        abort(403)

    if request.method == "POST":
        # Validaciones y normalizaciones
        nombre = request.form.get("nombre")
        if not nombre:
            flash("El campo 'nombre' es requerido")
            return redirect(url_for("app.edit_app", app_id=app_id))

        app.nombre = nombre
        app.descripcion = request.form.get("descripcion")
        app.tipo = request.form.get("tipo")
        app.stack = request.form.get("stack")
        app.framework = request.form.get("framework")
        app.repositorio_url = request.form.get("repositorio_url")
        app.estado = request.form.get("estado", "Activa")

        fecha_creacion_raw = request.form.get("fecha_creacion")
        if fecha_creacion_raw:
            try:
                app.fecha_creacion = datetime.fromisoformat(fecha_creacion_raw).date()
            except ValueError:
                try:
                    app.fecha_creacion = datetime.strptime(
                        fecha_creacion_raw, "%Y-%m-%d"
                    ).date()
                except Exception:
                    flash("Formato de fecha inválido")
                    return redirect(url_for("app.edit_app", app_id=app_id))

        owner_id_raw = request.form.get("owner_id")
        try:
            owner_id = int(owner_id_raw)
        except (TypeError, ValueError):
            flash("Owner inválido")
            return redirect(url_for("app.edit_app", app_id=app_id))

        owner = (
            User.query.join(Role)
            .filter(User.id == owner_id, Role.nombre == "Desarrollador")
            .first()
        )
        if not owner:
            flash("Usuario dueño no válido o no es Desarrollador")
            return redirect(url_for("app.edit_app", app_id=app_id))

        app.owner_id = owner_id

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar la aplicación: {e}")
            return redirect(url_for("app.edit_app", app_id=app_id))

        flash("Aplicación actualizada con éxito")
        return redirect(url_for("app.dashboard"))

    developers = User.query.join(Role).filter(Role.nombre == "Desarrollador").all()
    return render_template("dashboard/edit_app.html", app=app, users=developers)


def delete_app(app_id):
    app = db.session.get(Application, app_id)
    if not app:
        abort(404)
    if app.owner_id != current_user.id:
        abort(403)

    db.session.delete(app)
    db.session.commit()
    flash("Aplicación eliminada")
    return redirect(url_for("app.dashboard"))


def view_app(app_id):
    app = db.session.get(Application, app_id)
    if not app:
        abort(404)
    versions = (
        Version.query.filter_by(aplicacion_id=app_id)
        .order_by(Version.numero_version.desc())
        .all()
    )
    return render_template("dashboard/view_app.html", app=app, versions=versions)
