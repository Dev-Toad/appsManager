from app.config import db
from app.models.role import Role, Permission
from app.models.user import User
import click


def seed_roles_and_permissions():
    """Crea roles y permisos iniciales si no existen (con granularidad)."""

    permissions_data = {
        "admin:access": "Permite el acceso al dashboard administrativo.",
        "user:read": "Permite ver la lista de usuarios.",
        "user:create": "Permite crear nuevos usuarios.",
        "user:edit": "Permite modificar usuarios existentes (info, rol).",
        "user:view": "Permite ver el detalle del usuarios.",
        "user:toggle_status": "Permite activar o desactivar usuarios.",
        "user:assign_role": "Permite asignar roles a usuarios externos.",
        "app:read": "Permite ver la lista de aplicaciones y sus detalles.",
        "app:create": "Permite crear nuevas aplicaciones.",
        "app:edit": "Permite modificar aplicaciones existentes.",
        "app:view": "Permite ver el detalle del usuario.",
        "app:delete": "Permite eliminar aplicaciones.",
        "version:create": "Permite crear nuevas versiones de una aplicación.",
        "version:edit": "Permite editar versiones existentes.",
        "version:view": "Permite ver el detalle de la version existente.",
        "version:delete": "Permite eliminar versiones.",
        "role:manage": "Permite crear, editar y desactivar roles.",
        "app:manage": "Permite gestionar aplicaciones y versiones",
    }

    permissions_objects = {}

    for name, description in permissions_data.items():
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            permission = Permission(name=name, description=description)
            db.session.add(permission)
            print(f"  -> Creado Permiso: {name}")
        permissions_objects[name] = permission

    administrator_permissions = [
        permissions_objects["admin:access"],
        permissions_objects["role:manage"],
        permissions_objects["user:read"],
        permissions_objects["user:create"],
        permissions_objects["user:edit"],
        permissions_objects["user:view"],
        permissions_objects["user:toggle_status"],
        permissions_objects["app:read"],
        permissions_objects["app:create"],
        permissions_objects["app:edit"],
        permissions_objects["app:view"],
        permissions_objects["app:delete"],
        permissions_objects["version:create"],
        permissions_objects["version:edit"],
        permissions_objects["version:view"],
        permissions_objects["version:delete"],
        permissions_objects["user:assign_role"],
    ]

    roles_data = {
        "Administrator": administrator_permissions,
        "User": [permissions_objects["user:read"], permissions_objects["app:read"]],
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

        if name == "Administrator":
            obsolete_perm = permissions_objects.get("app:manage")
            if obsolete_perm in role.permissions:
                role.permissions.remove(obsolete_perm)
                print(f"    -> Removido permiso LEGADO: {obsolete_perm.name} de {name}")

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
        print(f"  -> Usuario {first_user.username} asignado como Administrator.")
    elif not first_user:
        print("  -> No se encontraron usuarios para asignar el rol de Administrador.")
    else:
        print(f"  -> El primer usuario ({first_user.username}) ya es Administrator.")


def register_commands(app):
    """Registra los comandos CLI personalizados en la aplicación Flask."""

    @app.cli.command("seed-db")
    def seed_db_command():
        print("--- Iniciando Seeding de Roles y Permisos ---")
        seed_roles_and_permissions()
        print("--- Asignando Rol de Administrador ---")
        assign_admin_to_first_user()
        click.echo("\n--- Tarea de Seeding Finalizada ---")
