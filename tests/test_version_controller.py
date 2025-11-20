import os
from app.config import create_app, db
from app.models.role import Role, Permission
from app.models.user import User
from app.models.application import Application
from app.models.version import Version


def setup_app_context():
    """Configura la aplicación y el contexto de base de datos en memoria."""
    # Usar una base de datos en memoria para pruebas
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    return app, ctx


def create_role_user_and_app():
    permission = Permission(
        name="manage_versions",
        description="Permite gestionar versiones de aplicaciones",
    )
    db.session.add(permission)
    db.session.commit()
    role = Role(name="Desarrollador")
    role.permissions.append(permission)
    db.session.add(role)
    db.session.commit()
    user = User(username="devv", email="devv@test.com", role_id=role.id)
    user.set_password("x")
    db.session.add(user)
    db.session.commit()

    # 4. Crear la Aplicación
    app_obj = Application(
        nombre="AppForVersion",
        descripcion="desc",
        owner_id=user.id,
        tipo_entorno="desarrollo",
    )
    db.session.add(app_obj)
    db.session.commit()
    return role, user, app_obj


def login_test_client(client, username):
    """Realiza el proceso de inicio de sesión."""
    return client.post(
        "/login",
        data={"username": username, "password": "x"},
        follow_redirects=True,
    )


def test_create_edit_delete_version():
    """
    Prueba el ciclo completo de creación, edición y eliminación de una versión
    de aplicación.
    """
    app, ctx = setup_app_context()
    try:
        # 1. Configuración inicial (Role, User, App) - ¡Ahora con permisos!
        role, user, app_obj = create_role_user_and_app()
        client = app.test_client()

        # 2. Iniciar sesión
        resp = login_test_client(client, user.username)
        assert resp.status_code == 200

        # --- Punto de fallo anterior: 3. Crear Versión ---
        # Ahora debería pasar el chequeo de permisos.
        resp = client.post(
            f"/app/{app_obj.id}/version/new",
            data={
                "numero_version": "1.0",
                "titulo": "v1",
                "descripcion": "desc",
                "documentacion_url": "http://doc",
                "gestor_bd": "none",
                "version_gestor_bd": "",
                "dependencias": "",
                "owner_id": str(user.id),
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        v = (
            db.session.query(Version)
            .filter_by(aplicacion_id=app_obj.id, numero_version="1.0")
            .first()
        )
        assert v is not None

        # 4. Editar Versión
        resp = client.post(
            f"/version/{v.id}/edit",
            data={
                "numero_version": v.numero_version,
                "titulo": "v1-edited",
                "descripcion": "desc2",
                "documentacion_url": "",
                "gestor_bd": "none",
                "version_gestor_bd": "",
                "dependencias": "",
                "owner_id": str(user.id),
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        v_edited = db.session.get(Version, v.id)
        assert v_edited.titulo == "v1-edited"

        # 5. Eliminar Versión
        resp = client.post(f"/version/{v_edited.id}/delete", follow_redirects=True)
        assert resp.status_code == 200
        v_deleted = db.session.get(Version, v_edited.id)
        assert v_deleted is None

    finally:
        db.session.remove()
        db.drop_all()
        ctx.pop()
