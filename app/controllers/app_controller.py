from app.config import db
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import current_user
from app.models import Version
from app.models.application import Application, ApplicationType
from sqlalchemy.exc import IntegrityError

from app.decorators import permissions_required
from app.form.aplication_form import EditApplicationForm, CreateApplicationForm
from sqlalchemy import desc, func

from sqlalchemy.orm import joinedload


def app_list():
    page = request.args.get("page", 1, type=int)
    per_page = 25

    search_query = request.args.get("q", "").strip()
    filter_type = request.args.get("type", "").strip()

    query = Application.query.options(joinedload(Application.application_type))

    if search_query:
        query = query.filter(Application.nombre.ilike(f"%{search_query}%"))

    if filter_type:
        query = query.join(Application.application_type).filter(
            ApplicationType.name == filter_type
        )

    pagination = query.order_by(
        desc(Application.updated_at),
        desc(Application.created_at),
        desc(Application.id),
    ).paginate(page=page, per_page=per_page, error_out=False)

    total_apps = query.order_by(None).count()

    counts_rows = (
        query.order_by(None)
        .join(Application.application_type)
        .with_entities(ApplicationType.name, func.count(Application.id))
        .group_by(ApplicationType.name)
        .all()
    )
    counts_by_type = {name: count for name, count in counts_rows}

    app_types = ApplicationType.query.order_by(ApplicationType.name).all()

    return render_template(
        "dashboard/applications/applications.html",
        apps=pagination.items,
        pagination=pagination,
        total_apps=total_apps,
        counts_by_type=counts_by_type,
        search_query=search_query,
        filter_type=filter_type,
        app_types=app_types,
    )


@permissions_required(["app:read"])
def view_app(app_id):
    """Muestra los detalles de una aplicación y sus versiones."""
    app = db.session.get(Application, app_id)
    if not app:
        abort(404)
    versions = (
        Version.query.filter_by(application_id=app_id)
        .order_by(Version.version_number.desc())
        .all()
    )
    return render_template(
        "dashboard/applications/view_app.html", app=app, versions=versions
    )


@permissions_required(["app:create"])
def new_app():
    form = CreateApplicationForm()

    if form.validate_on_submit():
        try:

            new_app = Application(
                nombre=form.nombre.data,
                descripcion=form.descripcion.data,
                repositorio_url=form.repositorio_url.data or None,
                version_docker=form.version_docker.data or None,
                estado=form.estado.data,
                tipo_entorno=form.tipo_entorno.data,
                application_type=form.application_type.data,
                stack_obj=form.stack_obj.data,
                framework_obj=form.framework_obj.data,
                owner=current_user,
            )

            db.session.add(new_app)
            db.session.commit()

            flash("Aplicación creada exitosamente.", "success")
            return redirect(url_for("app.view_app", app_id=new_app.id))

        except IntegrityError:
            db.session.rollback()
            flash("Error de integridad: Probablemente el nombre ya existe.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear la aplicación: {str(e)}", "danger")

    return render_template("dashboard/applications/new_app.html", form=form)


@permissions_required(["app:edit"])
def edit_app(app_id):
    app_obj = db.session.get(Application, app_id)
    if not app_obj:
        abort(404)

    form = EditApplicationForm(obj=app_obj, application_id=app_id)

    if form.validate_on_submit():
        try:
            form.populate_obj(app_obj)
            db.session.commit()

            flash("Aplicación actualizada con éxito", "success")
            return redirect(url_for("app.app_list"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {e}", "danger")

    return render_template(
        "dashboard/applications/edit_app.html", app=app_obj, form=form
    )


@permissions_required(["app:delete"])
def delete_app(app_id):
    app = db.session.get(Application, app_id)
    if not app:
        abort(404)

    if app.owner_id != current_user.id and current_user.role.name != "Administrator":
        abort(403)

    db.session.delete(app)
    db.session.commit()
    flash("Aplicación eliminada")
    return redirect(url_for("app.dashboard"))
