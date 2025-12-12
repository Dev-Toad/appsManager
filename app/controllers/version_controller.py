import os
from flask import render_template, redirect, url_for, flash, abort
from flask_login import current_user
from app.models import Version, Application
from app.config import db
from app.decorators import permissions_required
from app.form.version_form import CreateVersionForm, EditVersionForm
from sqlalchemy.exc import IntegrityError
from app.utils.file_helpers import save_version_file, delete_version_file
from flask import current_app, send_from_directory


def _cleanup_files(executable_path, docker_compose_path):
    if executable_path:
        delete_version_file(executable_path)
    if docker_compose_path:
        delete_version_file(docker_compose_path)


@permissions_required(["version:create"])
def new_version(app_id):
    """Crea una nueva versión para una aplicación."""
    app_instance = db.session.get(Application, app_id)
    if not app_instance:
        flash("Aplicación no encontrada.", "danger")
        return redirect(url_for("app.app_list"))

    form = CreateVersionForm()
    executable_path = None
    docker_compose_path = None

    def _process_file(file_field_data, version_number, file_type):
        """Intenta guardar el archivo. Lanza ValueError si falla la validación."""
        if file_field_data:
            try:
                return save_version_file(file_field_data, version_number, file_type)
            except ValueError as e:
                raise ValueError(f"Error en archivo de '{file_type}': {str(e)}")
        return None

    if form.validate_on_submit():
        try:
            executable_path = _process_file(
                form.executable_file.data, form.version_number.data, "executable"
            )

            docker_compose_path = _process_file(
                form.docker_compose_file.data,
                form.version_number.data,
                "docker_compose",
            )

            new_version = Version(
                version_number=form.version_number.data,
                title=form.title.data,
                description=form.description.data or None,
                documentacion_url=form.documentacion_url.data or None,
                executable_file_url=executable_path,
                docker_compose_url=docker_compose_path,
                docker_url=form.docker_url.data or None,
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

        except ValueError as e:
            _cleanup_files(executable_path, docker_compose_path)
            flash(f"{str(e)}", "danger")
            return render_template(
                "dashboard/version/new_version.html", form=form, app=app_instance
            )

        except IntegrityError:
            db.session.rollback()
            _cleanup_files(executable_path, docker_compose_path)
            flash("Ya existe una versión con ese número.", "danger")

        except Exception as e:
            db.session.rollback()
            _cleanup_files(executable_path, docker_compose_path)
            flash(f"Error al crear la versión: {str(e)}", "danger")

    return render_template(
        "dashboard/version/new_version.html", form=form, app=app_instance
    )


@permissions_required(["version:edit"])
def edit_version(version_id):
    """Edita una versión existente."""
    version = db.session.get(Version, version_id)

    if version is None:
        flash("La versión solicitada no fue encontrada.", "error")
        return redirect(url_for("index"))

    app_instance = version.application

    if app_instance is None:
        flash("No se pudo encontrar la aplicación asociada.", "error")
        return redirect(url_for("index"))

    form = EditVersionForm(obj=version, version_id=version_id)

    new_executable_path = None
    new_docker_compose_path = None
    files_to_delete_on_success = []

    if form.validate_on_submit():
        try:
            old_executable = version.executable_file_url
            old_docker_compose = version.docker_compose_url

            if form.executable_file.data:
                try:
                    new_executable_path = save_version_file(
                        form.executable_file.data,
                        form.version_number.data,
                        "executable",
                    )

                    if old_executable:
                        files_to_delete_on_success.append(old_executable)
                    version.executable_file_url = new_executable_path
                except ValueError as e:
                    flash(f"Error en archivo ejecutable: {str(e)}", "danger")
                    return render_template(
                        "dashboard/version/edit_version.html",
                        form=form,
                        version=version,
                        app=app_instance,
                    )

            elif form.keep_executable.data == "false" and old_executable:
                files_to_delete_on_success.append(old_executable)
                version.executable_file_url = None

            if form.docker_compose_file.data:
                try:
                    new_docker_compose_path = save_version_file(
                        form.docker_compose_file.data,
                        form.version_number.data,
                        "docker_compose",
                    )
                    if old_docker_compose:
                        files_to_delete_on_success.append(old_docker_compose)
                    version.docker_compose_url = new_docker_compose_path
                except ValueError as e:
                    _cleanup_files(new_executable_path, None)
                    flash(f"Error en archivo Docker Compose: {str(e)}", "danger")
                    return render_template(
                        "dashboard/version/edit_version.html",
                        form=form,
                        version=version,
                        app=app_instance,
                    )

            elif form.keep_docker_compose.data == "false" and old_docker_compose:
                files_to_delete_on_success.append(old_docker_compose)
                version.docker_compose_url = None

            version.version_number = form.version_number.data
            version.title = form.title.data
            version.description = form.description.data or None
            version.documentacion_url = form.documentacion_url.data or None
            version.db_manager = form.db_manager.data or None
            version.docker_url = form.docker_url.data or None
            version.db_manager_version = form.db_manager_version.data or None
            version.dependencias = form.dependencias.data or None
            version.support_start_date = form.support_start_date.data
            version.support_end_date = form.support_end_date.data

            db.session.commit()

            for file_path in files_to_delete_on_success:
                delete_version_file(file_path)

            flash(
                f"Versión {version.version_number} actualizada exitosamente.",
                "success",
            )

            return redirect(url_for("app.view_app", app_id=app_instance.id))

        except IntegrityError:
            db.session.rollback()
            _cleanup_files(new_executable_path, new_docker_compose_path)
            flash("Error: El número de versión ya existe.", "error")
        except Exception as e:
            db.session.rollback()
            _cleanup_files(new_executable_path, new_docker_compose_path)
            flash(f"Error al guardar los cambios: {str(e)}", "error")

    return render_template(
        "dashboard/version/edit_version.html",
        title=f"Editar Versión {version.version_number}",
        form=form,
        version=version,
        app=app_instance,
    )


def download_version_file(version_id, file_type):
    version = db.session.get(Version, version_id)
    if not version:
        abort(404)

    if file_type == "executable":
        rel_path = version.executable_file_url
    elif file_type == "docker_compose":
        rel_path = version.docker_compose_url
    else:
        abort(404)

    if not rel_path:
        abort(404)

    base_dir = current_app.config["UPLOAD_FOLDER"]
    directory, filename = os.path.split(rel_path)

    return send_from_directory(
        os.path.join(base_dir, directory),
        filename,
        as_attachment=True,
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
