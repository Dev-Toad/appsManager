from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.models import Version, Application, User, Role
from app.config import db


def new_version(app_id):
    app = db.session.get(Application, app_id)
    if not app:
        abort(404)

    if request.method == "POST":
        numero_version = request.form["numero_version"]
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        documentacion_url = request.form["documentacion_url"]
        gestor_bd = request.form["gestor_bd"]
        version_gestor_bd = request.form["version_gestor_bd"]
        dependencias = request.form["dependencias"]
        fecha_inicio_soporte = request.form.get("fecha_inicio_soporte")
        fecha_fin_soporte = request.form.get("fecha_fin_soporte")
        owner_id = request.form["owner_id"]

        owner = (
            User.query.join(Role)
            .filter(User.id == owner_id, Role.nombre == "Desarrollador")
            .first()
        )
        if not owner:
            flash("Usuario dueño no válido o no es Desarrollador")
            return redirect(url_for("version.new_version", app_id=app_id))

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
            owner_id=owner_id,
        )
        db.session.add(version)
        db.session.commit()
        flash("Versión creada con éxito")
        return redirect(url_for("app.view_app", app_id=app_id))

    developers = User.query.join(Role).filter(Role.nombre == "Desarrollador").all()
    return render_template("dashboard/new_version.html", app=app, users=developers)


def edit_version(version_id):
    version = db.session.get(Version, version_id)
    if not version:
        abort(404)
    if version.release_owner.id != current_user.id:
        abort(403)

    if request.method == "POST":
        version.titulo = request.form["titulo"]
        version.descripcion = request.form["descripcion"]
        version.documentacion_url = request.form["documentacion_url"]
        version.gestor_bd = request.form["gestor_bd"]
        version.version_gestor_bd = request.form["version_gestor_bd"]
        version.dependencias = request.form["dependencias"]
        version.fecha_inicio_soporte = request.form.get("fecha_inicio_soporte")
        version.fecha_fin_soporte = request.form.get("fecha_fin_soporte")
        version.owner_id = request.form["owner_id"]

        owner = (
            User.query.join(Role)
            .filter(User.id == version.owner_id, Role.nombre == "Desarrollador")
            .first()
        )
        if not owner:
            flash("Usuario dueño no válido o no es Desarrollador")
            return redirect(url_for("app.edit_version", version_id=version_id))

        db.session.commit()
        flash("Versión actualizada")
        return redirect(url_for("app.view_app", app_id=version.aplicacion_id))

    developers = User.query.join(Role).filter(Role.nombre == "Desarrollador").all()
    return render_template(
        "dashboard/edit_version.html", version=version, users=developers
    )


def delete_version(version_id):
    version = db.session.get(Version, version_id)
    if not version:
        abort(404)
    if version.release_owner.id != current_user.id:
        abort(403)

    app_id = version.aplicacion_id
    db.session.delete(version)
    db.session.commit()
    flash("Versión eliminada")
    return redirect(url_for("app.view_app", app_id=app_id))
