from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models.user import User
from app.config import db
from datetime import datetime


def index():
    if current_user.is_authenticated:
        return redirect(url_for("app.dashboard"))
    return redirect(url_for("app.login"))


def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.now()
            db.session.add(user)
            db.session.commit()

            return redirect(url_for("app.dashboard"))

        flash("Usuario o contraseña inválidos")

    return render_template("auth/login.html")


def logout():
    logout_user()
    return redirect(url_for("app.login"))
