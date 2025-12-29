from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, URL, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Role, User
from app.models.application import ApplicationType, Stack, Framework, Application
from app.config import db

APPLICATION_STATUSES = ["Activa", "En Desarrollo", "En Mantenimiento", "Retirada"]
ENVIRONMENT_TYPES = [
    "Desarrollo",
    "Pruebas/QA",
    "Staging/Pre-producción",
    "Producción",
    "Local",
]


def get_developer_users_query():
    """Retorna la consulta para todos los Usuarios que son Desarrolladores."""
    # return db.session.execute(db.select(User).join(Role)).scalars()
    return (
        db.session.execute(db.select(User).join(Role))
        .unique()
        .scalars()
    )

def get_app_types_query():
    """Retorna la consulta para todos los Tipos de Aplicación."""
    return db.session.execute(
        db.select(ApplicationType).order_by(ApplicationType.name)
    ).scalars()


def get_stacks_query():
    """Retorna la consulta para todos los Stacks Tecnológicos."""
    return db.session.execute(db.select(Stack).order_by(Stack.name)).scalars()


def get_frameworks_query():
    """Retorna la consulta para todos los Frameworks."""
    return db.session.execute(db.select(Framework).order_by(Framework.name)).scalars()


class BaseApplicationForm(FlaskForm):
    """Contiene todos los campos comunes entre Crear y Editar."""

    nombre = StringField(
        "Nombre",
        validators=[DataRequired(message="El nombre es obligatorio"), Length(max=100)],
    )
    descripcion = TextAreaField("Descripción", validators=[Optional()])
    repositorio_url = StringField(
        "URL del Repositorio",
        validators=[
            Optional(),
            URL(message="Debe ser una URL válida"),
            Length(max=255),
        ],
    )
    version_docker = StringField(
        "Versión Docker", validators=[Optional(), Length(max=50)]
    )

    estado = SelectField(
        "Estado",
        choices=[(status, status) for status in APPLICATION_STATUSES],
        validators=[DataRequired()],
    )

    tipo_entorno = SelectField(
        "Tipo de Entorno",
        choices=[(env, env) for env in ENVIRONMENT_TYPES],
        validators=[DataRequired()],
    )

    application_type = QuerySelectField(
        "Tipo de Aplicación",
        query_factory=get_app_types_query,
        get_pk=lambda t: t.id,
        get_label="name",
        allow_blank=False,
        validators=[DataRequired()],
    )

    stack_obj = QuerySelectField(
        "Stack Tecnológico",
        query_factory=get_stacks_query,
        get_pk=lambda s: s.id,
        get_label="name",
        allow_blank=False,
        validators=[DataRequired()],
    )

    framework_obj = QuerySelectField(
        "Framework",
        query_factory=get_frameworks_query,
        get_pk=lambda f: f.id,
        get_label="name",
        allow_blank=False,
        validators=[DataRequired()],
    )


class CreateApplicationForm(BaseApplicationForm):

    submit = SubmitField("Crear Aplicación")

    def validate_nombre(self, field):
        if Application.query.filter_by(nombre=field.data).first():
            raise ValidationError(
                "Ya existe una aplicación registrada con este nombre."
            )


class EditApplicationForm(BaseApplicationForm):

    owner = QuerySelectField(
        "Propietario",
        query_factory=get_developer_users_query,
        get_pk=lambda u: u.id,
        get_label=lambda u: u.username,
        allow_blank=False,
        validators=[DataRequired(message="El propietario es obligatorio")],
    )

    submit = SubmitField("Guardar Cambios")

    def __init__(self, *args, application_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.application_id = application_id

    def validate_nombre(self, field):
        existe = Application.query.filter(
            Application.nombre == field.data, Application.id != self.application_id
        ).first()

        if existe:
            raise ValidationError("Ya existe otra aplicación con este nombre.")
