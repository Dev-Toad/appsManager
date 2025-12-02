from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Optional, Length, ValidationError, URL
from app.models import Role, User, Version
from app.config import db


def get_developer_users_query():
    return db.session.execute(db.select(User).join(Role)).scalars()


class BaseVersionForm(FlaskForm):
    version_number = StringField(
        "Número de Versión",
        validators=[
            DataRequired(message="El número de versión es obligatorio"),
            Length(max=50),
        ],
        render_kw={"placeholder": "v1.0.0"},
    )

    title = StringField(
        "Título",
        validators=[DataRequired(message="El título es obligatorio"), Length(max=100)],
        render_kw={"placeholder": "Título descriptivo de la versión"},
    )

    description = TextAreaField(
        "Descripción",
        validators=[Optional()],
        render_kw={"placeholder": "Descripción detallada de los cambios"},
    )

    documentacion_url = StringField(
        "URL de Documentación",
        validators=[
            Optional(),
            URL(message="Debe ser una URL válida"),
            Length(max=255),
        ],
        render_kw={"placeholder": "https://docs.ejemplo.com/v1.0.0"},
    )

    db_manager = StringField(
        "Gestor de Base de Datos",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "PostgreSQL, MySQL, MongoDB..."},
    )

    db_manager_version = StringField(
        "Versión del Gestor",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "14.5, 8.0, 5.0..."},
    )

    dependencias = TextAreaField(
        "Dependencias",
        validators=[Optional()],
        render_kw={"placeholder": "requests==2.28.1\nflask==2.3.0\npandas>=1.5.0"},
    )

    support_start_date = DateField(
        "Fecha de Inicio de Soporte", validators=[Optional()], format="%Y-%m-%d"
    )

    support_end_date = DateField(
        "Fecha de Fin de Soporte", validators=[Optional()], format="%Y-%m-%d"
    )

    submit = SubmitField("Crear Versión")

    def validate(self, extra_validators=None):
        """Validación personalizada."""
        if not super().validate(extra_validators):
            return False

        if self.support_start_date.data and self.support_end_date.data:
            if self.support_end_date.data < self.support_start_date.data:
                self.support_end_date.errors.append(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )
                return False

        return True


class CreateVersionForm(BaseVersionForm):

    submit = SubmitField("Crear Versión")

    def validate_title(self, field):
        if Version.query.filter_by(title=field.data).first():
            raise ValidationError(
                "Ya existe una aplicación registrada con este nombre."
            )


class EditVersionForm(BaseVersionForm):
    """
    Formulario para editar una Versión existente.

    Permite modificar todos los campos y cambiar el Propietario (Owner).
    """

    submit = SubmitField("Guardar Cambios")

    def __init__(self, *args, version_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.version_id = version_id

    def validate_version_number(self, field):
        """Valida que el número de versión sea único para la aplicación."""
        if self.version_id:

            existing = Version.query.filter(
                Version.version_number == field.data, Version.id != self.version_id
            ).first()

            if existing:
                raise ValidationError("Ya existe otra versión con este número.")

    def validate(self, extra_validators=None):
        """Validación personalizada."""
        if not super().validate(extra_validators):
            return False

        if self.support_start_date.data and self.support_end_date.data:
            if self.support_end_date.data < self.support_start_date.data:
                self.support_end_date.errors.append(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )
                return False

        return True
