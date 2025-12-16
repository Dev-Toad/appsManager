from app.config import db
from datetime import datetime


APPLICATION_STATUSES = ["Activa", "En Desarrollo", "En Mantenimiento", "Retirada"]
# ENVIRONMENT_TYPES = ["Servidor", "Cloud", "Kubernetes", "Local"]

ENVIRONMENT_TYPES = [
    "Desarrollo",
    "Pruebas/QA",
    "Staging/Pre-producción",
    "Producción",
    "Local",
]


class Stack(db.Model):
    """
    Modelo para los Stacks Tecnológicos (e.g., Python, Java, JavaScript).
    """

    __tablename__ = "stacks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    frameworks = db.relationship("Framework", backref="stack", lazy="dynamic")
    applications = db.relationship("Application", backref="stack_obj", lazy="dynamic")

    def __repr__(self):
        return f"<Stack {self.name}>"


class Framework(db.Model):

    __tablename__ = "frameworks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),  nullable=False)

    stack_id = db.Column(
        db.Integer, db.ForeignKey("stacks.id"), nullable=False, index=True
    )

    applications = db.relationship(
        "Application", backref="framework_obj", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Framework {self.name}>"


class ApplicationType(db.Model):
    __tablename__ = "application_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    applications = db.relationship(
        "Application", backref="application_type", lazy="dynamic"
    )

    def __repr__(self):
        return f"<ApplicationType {self.name}>"


class Application(db.Model):

    __tablename__ = "aplicaciones"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    type_id = db.Column(
        db.Integer, db.ForeignKey("application_types.id"), nullable=False, index=True
    )

    estado = db.Column(
        db.Enum(*APPLICATION_STATUSES, name="app_status"),
        default="Activa",
        nullable=False,
    )

    tipo_entorno = db.Column(
        db.Enum(*ENVIRONMENT_TYPES, name="env_type"),
        default="Desarrollo",
        nullable=False,
    )

    stack_id = db.Column(
        db.Integer, db.ForeignKey("stacks.id"), nullable=False, index=True
    )

    framework_id = db.Column(
        db.Integer, db.ForeignKey("frameworks.id"), nullable=False, index=True
    )

    repositorio_url = db.Column(db.String(255))
    version_docker = db.Column(db.String(50))

    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    owner = db.relationship("User", back_populates="owned_apps", lazy="joined")

    versions = db.relationship(
        "Version",
        back_populates="application",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Application(id={self.id}, nombre='{self.nombre}', estado='{self.estado}')>"

    @property
    def is_active(self):
        """Indica si la aplicación está activa."""
        return self.estado == "Activa"

    def to_dict(self):
        """Retorna una representación serializable (diccionario) del objeto."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "tipo": self.application_type.name if self.application_type else None,
            "stack": self.stack_obj.name if self.stack_obj else None,
            "framework": self.framework_obj.name if self.framework_obj else None,
            "repositorio_url": self.repositorio_url,
            "version_docker": self.version_docker,
            "owner_id": self.owner_id,
            "tipo_entorno": self.tipo_entorno,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner_username": self.owner.username if self.owner else None,
        }
