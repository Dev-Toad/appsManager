from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    EqualTo,
    ValidationError,
)
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models.role import Role


def get_all_roles():
    """Consulta todas las roles activos para el QuerySelectField."""
    return Role.query.filter_by(active=True).all()


class CreateUserForm(FlaskForm):
    """Formulario para la creación inicial de un usuario. La contraseña es obligatoria."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El email es obligatorio."),
            Email(message="Formato de email inválido."),
        ],
    )
    username = StringField(
        "Nombre de Usuario",
        validators=[
            DataRequired(message="El nombre de usuario es obligatorio."),
            Length(
                min=4, message="El nombre de usuario debe tener al menos 4 caracteres"
            ),
        ],
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria en la creación."),
            Length(min=6, message="La contraseña debe tener al menos 6 caracteres"),
        ],
    )
    password_confirm = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(message="Debe confirmar la contraseña."),
            EqualTo("password", message="Las contraseñas deben coincidir."),
        ],
    )

    full_name = StringField("Nombre Completo", validators=[Optional(), Length(max=120)])

    role = QuerySelectField(
        "Rol a Asignar",
        query_factory=get_all_roles,
        get_pk=lambda r: r.id,
        get_label=lambda r: r.name,
        validators=[DataRequired(message="Debe asignar un rol.")],
    )

    is_active = BooleanField("Activo", default=True)


class EditUserForm(CreateUserForm):
    """
    Formulario para editar un usuario existente.
    Hereda de CreateUserForm, pero anula los campos de contraseña para hacerlos opcionales.
    """

    password = PasswordField(
        "Nueva Contraseña",
        validators=[
            Optional(),
            Length(
                min=6,
                message="La contraseña debe tener al menos 6 caracteres si se ingresa.",
            ),
        ],
    )

    password_confirm = PasswordField(
        "Confirmar Nueva Contraseña",
        validators=[
            Optional(),
            EqualTo("password", message="Las contraseñas deben coincidir."),
        ],
    )

    def validate_password_confirm(self, field):
        if field.data and not self.password.data:
            raise ValidationError(
                "Debes ingresar la nueva contraseña en el campo superior para confirmarla."
            )
