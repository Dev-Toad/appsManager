from app.config import db

class SOCompatible(db.Model):
    __tablename__ = 'sistemas_operativos_compatibles'
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('versiones.id'), nullable=False)
    nombre_so = db.Column(db.String(100))

    # ✅ Relación inversa - ¡Esta es la que falta!
    version = db.relationship('Version', back_populates='so_compatibles')

    def __repr__(self):
        return f'<SOCompatible {self.nombre_so} for Version {self.version_id}>'