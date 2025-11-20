from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
from app.models.role import Role
from wtforms_sqlalchemy.fields import QuerySelectField


def get_all_roles():
    return Role.query.filter_by(active=True).all()


class UserForm(FlaskForm):
    # Información de Cuenta
    email = StringField(
        "Email", validators=[DataRequired(message="El email es obligatorio."), Email()]
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
