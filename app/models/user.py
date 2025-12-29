from app.config import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=True)

    avatar_url = db.Column(db.String(256), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    role_id = db.Column(
        db.Integer, db.ForeignKey("roles.id"), nullable=True, index=True
    )

    role = db.relationship("Role", back_populates="users", lazy="joined")

    is_active = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    external_user_id = db.Column(db.Integer, unique=True, index=True, nullable=True)

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

    def can(self, permission_name):
        if self.role is not None:
            return self.role.has_permission(permission_name)
        return False

    def __repr__(self):
        return f"<User {self.username}>"
