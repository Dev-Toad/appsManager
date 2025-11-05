from app.config import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'aplicaciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.Date, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='Activa')
    tipo = db.Column(db.String(50))
    stack = db.Column(db.String(50))
    framework = db.Column(db.String(50))
    repositorio_url = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tipo_entorno = db.Column(db.String(50), default='servidor', nullable=False)
    version_docker = db.Column(db.String(50))
    
    # Relaciones
    owner = db.relationship('User', back_populates='owned_apps', lazy=True)
    versions = db.relationship('Version', back_populates='application', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Application {self.nombre}>'