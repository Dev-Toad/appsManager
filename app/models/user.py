# app/models/user.py

from app.config import (
    db,
    login_manager,
)  # ← Esto YA NO causará ciclo si lo moviste en config/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    # Use Session.get (requires SQLAlchemy >= 1.4)
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relaciones
    owned_apps = db.relationship(
        "Application",
        foreign_keys="Application.owner_id",
        back_populates="owner",
        lazy=True,
    )

    owned_versions = db.relationship(
        "Version",
        foreign_keys="Version.owner_id",
        back_populates="release_owner",
        lazy=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
