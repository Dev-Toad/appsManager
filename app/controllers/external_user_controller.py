from flask import request, render_template, redirect, url_for, flash
from app.config import db
from app.models.external_user import ExternalUser
from app.models.user import User
from app.models.role import Role

from app.decorators import permissions_required


@permissions_required("user:assign_role")
def assign_role_to_external_user():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        role_id = int(request.form.get("role_id"))

        ext = ExternalUser.query.filter(
            db.func.lower(db.func.trim(ExternalUser.email)) == email
        ).first()

        if not ext:
            flash("No existe ese usuario en la base externa.", "error")
            return redirect(url_for("external.assign_role_to_external_user"))

        role = db.session.get(Role, role_id)
        if not role:
            flash("Rol inválido.", "error")
            return redirect(url_for("external.assign_role_to_external_user"))

        existing = User.query.filter_by(external_user_id=ext.admin_usuario_id).first()

        if existing:

            existing.role_id = role.id
            existing.is_active = True
            existing.email = (ext.email or "").strip().lower()
            existing.full_name = ext.nombre
            db.session.commit()

            flash("Rol actualizado correctamente.", "success")
            return redirect(url_for("user.list_users"))

        local_user = User(
            username=(ext.email or "").strip().lower(),
            password_hash="EXTERNAL_AUTH",
            external_user_id=ext.admin_usuario_id,
            email=(ext.email or "").strip().lower(),
            full_name=ext.nombre,
            role_id=role.id,
            is_active=True,
        )
        db.session.add(local_user)
        db.session.commit()

        flash("Rol asignado correctamente.", "success")
        return redirect(url_for("user.list_users"))

    roles = Role.query.all()
    return render_template("dashboard/users/assign_role.html", roles=roles)
