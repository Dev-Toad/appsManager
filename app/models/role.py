from app.config import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship("User", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.nombre}>"
