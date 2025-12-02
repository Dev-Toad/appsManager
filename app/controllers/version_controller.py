from flask import render_template, redirect, url_for, flash, abort
from flask_login import current_user
from app.models import Version, Application
from app.config import db
from app.decorators import permissions_required
from app.form.version_form import CreateVersionForm, EditVersionForm
from sqlalchemy.exc import IntegrityError


@permissions_required(["version:create"])
def new_version(app_id):
    """Crea una nueva versión para una aplicación."""
    app_instance = db.session.get(Application, app_id)
    if not app_instance:
        flash("Aplicación no encontrada.", "danger")
        return redirect(url_for("app.app_list"))

    form = CreateVersionForm()

    if form.validate_on_submit():
        try:
            new_version = Version(
                version_number=form.version_number.data,
                title=form.title.data,
                description=form.description.data or None,
                documentacion_url=form.documentacion_url.data or None,
                db_manager=form.db_manager.data or None,
                db_manager_version=form.db_manager_version.data or None,
                dependencias=form.dependencias.data or None,
                support_start_date=form.support_start_date.data,
                support_end_date=form.support_end_date.data,
                release_owner=current_user,
                application_id=app_id,
            )

            db.session.add(new_version)
            db.session.commit()

            flash(
                f"Versión {new_version.version_number} creada exitosamente.",
                "success",
            )
            return redirect(url_for("app.view_app", app_id=app_id))

        except IntegrityError:
            db.session.rollback()
            flash("Ya existe una versión con ese número.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear la versión: {str(e)}", "danger")

    return render_template(
        "dashboard/version/new_version.html", form=form, app=app_instance
    )


@permissions_required(["version:edit"])
def edit_version(version_id):
    """
    Controlador para editar una versión de aplicación existente.
    Carga la Versión y su Aplicación asociada para el contexto de la plantilla.
    """

    version = db.session.get(Version, version_id)

    if version is None:
        flash("La versión solicitada no fue encontrada.", "error")
        return redirect(url_for("index"))

    app_instance = version.application

    if app_instance is None:
        flash("No se pudo encontrar la aplicación asociada a esta versión.", "error")
        return redirect(url_for("index"))

    form = EditVersionForm(obj=version)

    if form.validate_on_submit():
        try:
            version.version_number = form.version_number.data
            version.title = form.title.data
            version.description = form.description.data
            version.documentacion_url = form.documentacion_url.data
            version.db_manager = form.db_manager.data
            version.db_manager_version = form.db_manager_version.data
            version.dependencias = form.dependencias.data
            version.support_start_date = form.support_start_date.data
            version.support_end_date = form.support_end_date.data

            db.session.commit()
            flash(
                f"La Versión {version.version_number} de {app_instance.nombre}"
                "ha sido actualizada.",
                "success",
            )

            return redirect(url_for("app.view_app", app_id=app_instance.id))

        except IntegrityError:
            db.session.rollback()
            flash(
                "Error: El número de versión ya existe para esta aplicación.", "error"
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar los cambios: {str(e)}", "error")

    return render_template(
        "dashboard/version/edit_version.html",
        title=f"Editar Versión {version.version_number}",
        form=form,
        version=version,
        app=app_instance,
    )


@permissions_required(["version:delete"])
def delete_version(version_id):
    """Permite eliminar una versión existente."""
    version = db.session.get(Version, version_id)
    if not version:
        abort(404)

    if (
        version.release_owner.id != current_user.id
        and current_user.role.name != "Administrator"
    ):
        abort(403)

    app_id = version.application
    db.session.delete(version)
    db.session.commit()
    flash("Versión eliminada")
    return redirect(url_for("app.view_app", app_id=app_id))
