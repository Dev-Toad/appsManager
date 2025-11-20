from flask import render_template, request, redirect, url_for, flash, abort
from app.models import Role
from app.config import db
from app.decorators import permissions_required
from app.form.role_forms import RoleForm


@permissions_required(["admin:access", "role:manage"])
def list_roles():
    """Muestra todos los roles."""
    roles = Role.query.all()
    return render_template(
        "dashboard/roles/list_roles.html",
        roles=roles,
        active_page="roles",
        hasattr=hasattr,
    )


@permissions_required(["role:manage"])
def new_role():
    form = RoleForm()
    if form.validate_on_submit():
        name = form.name.data
        descripcion = form.descripcion.data

        if Role.query.filter_by(name=name).first():
            flash(
                f"El rol con nombre '{name}' ya existe. Por favor, elige otro.",
                "warning",
            )
            return render_template("dashboard/roles/new_role.html", form=form)

        new_role = Role(name=name, descripcion=descripcion)

        new_role.permissions = form.permissions.data

        db.session.add(new_role)
        db.session.commit()
        flash(f"Rol '{name}' creado con éxito.", "success")
        return redirect(url_for("rol.list_roles"))

    return render_template("dashboard/roles/new_role.html", form=form)


@permissions_required(["role:manage"])
def edit_role(role_id):
    """Formulario y lógica para editar un rol y sus permisos (usando Flask-WTF)."""

    role = db.session.get(Role, role_id)
    if not role:
        abort(404)

    form = RoleForm(obj=role)
    if request.method == "GET":
        form.permissions.data = role.permissions

    if form.validate_on_submit():
        name = form.name.data
        descripcion = form.descripcion.data

        if Role.query.filter(Role.name == name, Role.id != role_id).first():
            flash(f"El rol con nombre '{name}' ya existe.", "warning")
            return render_template(
                "dashboard/roles/edit_role.html", role=role, form=form
            )

        role.name = name
        role.descripcion = descripcion

        role.permissions = form.permissions.data

        db.session.commit()
        flash(f"Rol '{name}' actualizado con éxito.", "success")
        return redirect(url_for("rol.list_roles"))

    return render_template("dashboard/roles/edit_role.html", role=role, form=form)


@permissions_required(["role:manage"])
def toggle_role_status(role_id):
    """Activa o desactiva un rol cambiando su estado (activo/inactivo)."""

    role = db.session.get(Role, role_id)
    if not role:
        abort(404)

    role.active = not role.active

    action = "activado" if role.active else "desactivado"

    db.session.commit()

    flash(f"Rol '{role.name}' {action} con éxito.", "info")

    return redirect(url_for("rol.list_roles"))


@permissions_required(["admin:access", "role:manage"])
def view_role(role_id):
    """Muestra los detalles de un rol específico, incluyendo sus permisos."""
    role = db.session.get(Role, role_id)
    if not role:
        abort(404)

    return render_template("dashboard/roles/view_role.html", role=role)
