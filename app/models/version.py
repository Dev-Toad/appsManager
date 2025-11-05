from app.config import db
from datetime import datetime

class Version(db.Model):
    __tablename__ = 'versiones'
    id = db.Column(db.Integer, primary_key=True)
    aplicacion_id = db.Column(db.Integer, db.ForeignKey('aplicaciones.id'), nullable=False)
    numero_version = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    documentacion_url = db.Column(db.String(255))
    gestor_bd = db.Column(db.String(50))
    version_gestor_bd = db.Column(db.String(50))
    dependencias = db.Column(db.Text)
    fecha_inicio_soporte = db.Column(db.Date)
    fecha_fin_soporte = db.Column(db.Date)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones - ✅ Todo con back_populates
    application = db.relationship('Application', back_populates='versions', lazy=True)
    release_owner = db.relationship('User', back_populates='owned_versions', lazy=True)
    so_compatibles = db.relationship('SOCompatible', back_populates='version', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Version {self.numero_version} of App {self.aplicacion_id}>'