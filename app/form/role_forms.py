from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from app.models import Permission
from wtforms import widgets


def get_all_permissions():
    """Retorna todos los objetos de Permission."""
    return Permission.query.all()


def get_permission_label(permission):
    """Retorna el nombre del permiso para mostrarlo en el checkbox."""
    return permission.name


class RoleForm(FlaskForm):
    name = StringField(
        "Nombre del Rol",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=2, max=50),
        ],
        render_kw={"placeholder": "Ej. Administrador, Editor"},
    )

    descripcion = TextAreaField(
        "Descripción",
        validators=[Length(max=255)],
        render_kw={"placeholder": "Descripción breve del propósito del rol"},
    )

    permissions = QuerySelectMultipleField(
        "Permisos",
        query_factory=lambda: Permission.query.all(),
        get_label="name",
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
    )
    submit = SubmitField("Guardar Cambios")
