from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from datetime import datetime
import hashlib
from sqlalchemy import func, or_

from app.config import db
from app.models.user import User
from app.models.external_user import ExternalUser
from app.models.role import Role


EXTERNAL_SENTINEL = "EXTERNAL_AUTH"
DEFAULT_ROLE_NAME = "User"


def check_password_md5(plain_password: str, stored_md5_hex: str) -> bool:
    if not stored_md5_hex:
        return False
    stored = stored_md5_hex.strip().lower()
    candidate = hashlib.md5(plain_password.encode("utf-8")).hexdigest()
    return candidate == stored


def _get_default_role():
    return Role.query.filter(func.lower(Role.name) == DEFAULT_ROLE_NAME.lower()).first()


def _redirect_after_login(user):

    if (
        getattr(user, "role", None)
        and getattr(user.role, "name", None) == "Administrador"
    ):
        return redirect(url_for("app.dashboard"))
    return redirect(url_for("app.app_list"))


def index():
    if current_user.is_authenticated:
        return _redirect_after_login(current_user)
    return redirect(url_for("app.login"))


def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            flash("Completa email y contraseña.")
            return render_template("auth/login.html"), 400

        local_admin = User.query.filter(func.lower(User.email) == email).first()
        is_local_admin = bool(
            local_admin
            and local_admin.role
            and local_admin.role.name == "Administrador"
            and (local_admin.password_hash or "") != EXTERNAL_SENTINEL
        )

        if is_local_admin:
            if local_admin.check_password(password):
                login_user(local_admin)
                local_admin.last_login = datetime.now()
                db.session.commit()
                return _redirect_after_login(local_admin)

            flash("Usuario o contraseña inválidos")
            return render_template("auth/login.html"), 401

        ext = ExternalUser.query.filter(
            func.lower(func.trim(ExternalUser.email)) == email,
            ExternalUser.admin_tipo_id.in_([7, 6, 3]),
            or_(
                ExternalUser.fecha_expiracion.is_(None),
                ExternalUser.fecha_expiracion > func.now(),
            ),
        ).first()

        if not ext:
            flash("No tienes acceso al sistema.", "danger")
            return render_template("auth/login.html"), 403

        if not check_password_md5(password, ext.password):
            flash("Usuario o contraseña inválidos")
            return render_template("auth/login.html"), 401

        default_role = _get_default_role()
        if not default_role:
            flash(f"Falta el rol '{DEFAULT_ROLE_NAME}'. Créalo en Roles.", "danger")
            return render_template("auth/login.html"), 500

        local_user = User.query.filter_by(external_user_id=ext.admin_usuario_id).first()

        if not local_user:
            local_user = User(
                username=(ext.email or "").strip().lower(),
                password_hash=EXTERNAL_SENTINEL,
                external_user_id=ext.admin_usuario_id,
                email=(ext.email or "").strip().lower(),
                full_name=ext.nombre,
                is_active=True,
                role_id=default_role.id,
            )
            db.session.add(local_user)
            db.session.commit()
        else:
            if not local_user.is_active:
                flash("Usuario deshabilitado en este sistema.")
                return render_template("auth/login.html"), 403

            if not local_user.role_id:
                local_user.role_id = default_role.id

            local_user.email = (ext.email or "").strip().lower()
            local_user.full_name = ext.nombre
            local_user.last_login = datetime.now()
            db.session.commit()

        login_user(local_user)
        return _redirect_after_login(local_user)

    return render_template("auth/login.html")


def logout():
    logout_user()
    return redirect(url_for("app.login"))
