from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    DateField,
    RadioField,
)
from wtforms.validators import DataRequired, Optional, Length, ValidationError, URL
from flask_wtf.file import FileField, FileAllowed
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
    )

    title = StringField(
        "Título de la Versión",
        validators=[
            DataRequired(message="El título es obligatorio"),
            Length(max=100),
        ],
    )

    description = TextAreaField(
        "Descripción",
        validators=[Optional()],
    )

    documentacion_url = StringField(
        "URL de Documentación",
        validators=[
            Optional(),
            URL(message="Debe ser una URL válida"),
            Length(max=255),
        ],
    )

    db_manager = StringField(
        "Gestor de Base de Datos",
        validators=[Optional(), Length(max=50)],
    )

    db_manager_version = StringField(
        "Versión del Gestor de BD",
        validators=[Optional(), Length(max=50)],
    )

    dependencias = TextAreaField(
        "Dependencias",
        validators=[Optional()],
    )

    support_start_date = DateField(
        "Fecha de inicio de soporte",
        format="%Y-%m-%d",
        validators=[Optional()],
    )

    support_end_date = DateField(
        "Fecha de fin de soporte",
        format="%Y-%m-%d",
        validators=[Optional()],
    )


class CreateVersionForm(BaseVersionForm):
    executable_file = FileField(
        "Archivo ejecutable (.deb)",
        validators=[
            Optional(),
            FileAllowed(["deb"], "Solo se permiten archivos .deb"),
        ],
    )

    docker_compose_file = FileField(
        "Archivo Docker Compose",
        validators=[
            Optional(),
            FileAllowed(["yml", "yaml"], "Solo se permiten archivos .yml / .yaml"),
        ],
    )

    submit = SubmitField("Crear Versión")

    def __init__(self, *args, application_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.application_id = application_id

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if self.support_start_date.data and self.support_end_date.data:
            if self.support_end_date.data < self.support_start_date.data:
                self.support_end_date.errors.append(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )
                return False

        return True


class EditVersionForm(BaseVersionForm):
    executable_file = FileField(
        "Nuevo archivo ejecutable (.deb)",
        validators=[
            Optional(),
            FileAllowed(["deb"], "Solo se permiten archivos .deb"),
        ],
    )

    docker_compose_file = FileField(
        "Nuevo archivo Docker Compose",
        validators=[
            Optional(),
            FileAllowed(["yml", "yaml"], "Solo se permiten archivos .yml / .yaml"),
        ],
    )

    keep_executable = RadioField(
        "Archivo ejecutable actual",
        choices=[
            ("true", "Mantener archivo actual"),
            ("false", "Eliminar archivo actual"),
        ],
        default="true",
    )

    keep_docker_compose = RadioField(
        "Archivo docker-compose actual",
        choices=[
            ("true", "Mantener archivo actual"),
            ("false", "Eliminar archivo actual"),
        ],
        default="true",
    )

    submit = SubmitField("Guardar Cambios")

    def __init__(self, *args, version_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.version_id = version_id

    def validate_version_number(self, field):
        if self.version_id:
            existing = (
                Version.query.filter(
                    Version.version_number == field.data,
                    Version.id != self.version_id,
                )
                .limit(1)
                .first()
            )
            if existing:
                raise ValidationError("Ya existe otra versión con este número.")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if self.support_start_date.data and self.support_end_date.data:
            if self.support_end_date.data < self.support_start_date.data:
                self.support_end_date.errors.append(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )
                return False

        return True
