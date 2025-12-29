from app.config import db


class ExternalUser(db.Model):
    __bind_key__ = "external"
    __tablename__ = "admin_usuario"

    admin_usuario_id = db.Column(db.Integer, primary_key=True)
    admin_tipo_id = db.Column(db.Integer, nullable=False)

    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    nombre = db.Column(db.Text, nullable=False)

    fecha_expiracion = db.Column(db.DateTime, nullable=True)

    puede_marcar = db.Column(db.Boolean, nullable=False, default=False)
