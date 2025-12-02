from app.config import db
from sqlalchemy.sql import func


class Version(db.Model):
    __tablename__ = "versions"
    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer, db.ForeignKey("aplicaciones.id"), nullable=False, index=True
    )

    version_number = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    documentacion_url = db.Column(db.String(255))

    db_manager = db.Column(db.String(50))
    db_manager_version = db.Column(db.String(50))

    dependencias = db.Column(db.Text)

    support_start_date = db.Column(db.Date)
    support_end_date = db.Column(db.Date)

    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    application = db.relationship("Application", back_populates="versions", lazy=True)
    release_owner = db.relationship("User", back_populates="owned_versions", lazy=True)
    so_compatibles = db.relationship(
        "SOCompatible",
        back_populates="version",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Version {self.version_number} of App {self.application_id}>"
