from app.config import db
from app.models.role import Role, Permission
from app.models.user import User
import click


def seed_roles_and_permissions():
    """Crea roles y permisos iniciales si no existen."""

    permissions_data = {
        "admin:access": "Permite el acceso al dashboard administrativo.",
        "user:read": "Permite ver la información básica de usuarios.",
        "user:create": "Permite crear nuevos usuarios.",
        "app:manage": "Permite gestionar aplicaciones y versiones.",
        "role:manage": "Permite crear, editar y desactivar roles.",
    }

    permissions_objects = {}

    for name, description in permissions_data.items():
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            permission = Permission(name=name, description=description)
            db.session.add(permission)
            print(f"  -> Creado Permiso: {name}")
        permissions_objects[name] = permission

    roles_data = {
        "Administrator": [
            permissions_objects["admin:access"],
            permissions_objects["user:read"],
            permissions_objects["user:create"],
            permissions_objects["app:manage"],
            permissions_objects["role:manage"],
        ],
        "User": [permissions_objects["user:read"]],
    }

    for name, required_permissions in roles_data.items():
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, descripcion=f"Rol principal de {name}")
            db.session.add(role)
            print(f"  -> Creado Rol: {name}")

        for perm in required_permissions:
            if perm not in role.permissions:
                role.permissions.append(perm)
                print(f"    -> Asignado {perm.name} a {name}")

    db.session.commit()


def assign_admin_to_first_user():
    """Asigna el rol de Administrador al primer usuario encontrado."""
    admin_role = Role.query.filter_by(name="Administrator").first()
    first_user = User.query.order_by(User.id.asc()).first()

    if (
        first_user
        and admin_role
        and (first_user.role_id is None or first_user.role_id != admin_role.id)
    ):
        first_user.role_id = admin_role.id
        db.session.commit()
    elif not first_user:
        pass


def register_commands(app):
    """Registra los comandos CLI personalizados en la aplicación Flask."""

    @app.cli.command("seed-db")
    def seed_db_command():
        seed_roles_and_permissions()
        assign_admin_to_first_user()
        click.echo("\n--- Tarea de Seeding Finalizada ---")
