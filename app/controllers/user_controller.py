from flask import render_template, redirect, url_for, flash, abort
from flask_login import current_user
from app.config import db
from app.models.user import User
from app.models.role import Role
from app.decorators import permissions_required
from sqlalchemy.orm import joinedload
from app.form.user_form import CreateUserForm, EditUserForm


@permissions_required(["user:read"])
def list_users():
    """Muestra la lista de todos los usuarios, cargando roles de forma eficiente."""
    users = (
        db.session.execute(db.select(User).options(joinedload(User.role)))
        .unique()
        .scalars()
        .all()
    )

    roles = Role.query.all()

    return render_template(
        "dashboard/users/list_users.html", users=users, roles=roles, active_page="users"
    )


@permissions_required(["admin:access", "user:create"])
def new_user():

    form = CreateUserForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data

        try:
            new_user = User(
                username=username,
                email=email,
                full_name=form.full_name.data,
                role_id=form.role.data.id,
                is_active=form.is_active.data,
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash(f"Usuario '{username}' creado con éxito.", "success")
            return redirect(url_for("user.list_users"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear usuario Mensaje: {str(e)[:100]}...", "danger")
            return render_template(
                "dashboard/users/new_user.html", form=form, active_page="users"
            )

    return render_template(
        "dashboard/users/new_user.html", form=form, active_page="users"
    )


@permissions_required(["admin:access", "user:view"])
def view_user(user_id):
    user = (
        db.session.execute(
            db.select(User).where(User.id == user_id).options(joinedload(User.role))
        )
        .unique()
        .scalar_one_or_none()
    )

    if not user:
        abort(404)

    return render_template(
        "dashboard/users/view_user.html", user=user, active_page="users"
    )


@permissions_required(["admin:access", "user:edit"])
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    form = EditUserForm(obj=user)

    if form.validate_on_submit():

        new_username = form.username.data
        new_email = form.email.data
        try:
            user.username = new_username
            user.email = new_email
            user.full_name = form.full_name.data
            user.is_active = form.is_active.data
            user.role = form.role.data

            if form.password.data:
                user.set_password(form.password.data)

            db.session.commit()
            flash(f"Usuario '{user.username}' actualizado con éxito.", "success")
            return redirect(url_for("user.list_users"))

        except Exception as e:
            db.session.rollback()
            error_code = 500
            print(f"Error al actualizar usuario: {e}")
            flash(
                f"Error {error_code} al actualizar usuario. Inténtalo de nuevo.",
                "danger",
            )

    return render_template(
        "dashboard/users/edit_user.html", user=user, form=form, active_page="users"
    )


@permissions_required(["admin:access", "user:toggle_status"])
def toggle_user_status(user_id):
    """Activa o desactiva la cuenta de un usuario."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    if user.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "warning")
        return redirect(url_for("user.list_users"))

    user.is_active = not user.is_active
    action = "activada" if user.is_active else "desactivada"

    db.session.commit()
    flash(f"Cuenta de usuario '{user.username}' {action} con éxito.", "info")

    return redirect(url_for("user.list_users"))
