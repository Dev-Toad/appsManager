import os
import pytest
from app.config import create_app, db
from app.models.role import Role, Permission
from app.models.user import User
from app.models.application import Application


@pytest.fixture(scope="function")
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    # Necesario para que Flask-Flash funcione y para el contexto de la base de datos
    app.config["SECRET_KEY"] = "testing-key"
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        yield app
        # Eliminar todas las tablas al finalizar la función
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Fixture que proporciona un cliente de test para cada función."""
    return app.test_client()


@pytest.fixture(scope="function")
def setup_roles_and_users(app):
    """
    Crea roles, permisos y usuarios Admin/Developer para las pruebas.
    Asigna 'app:manage' al Administrador y 'app:create' al Desarrollador.
    """
    with app.app_context():
        # --- 1. Crear Permisos ---
        perm_create = Permission(name="app:create", description="Crear aplicaciones")
        perm_manage = Permission(
            name="app:manage", description="Gestionar (CRUD) aplicaciones"
        )
        perm_admin = Permission(name="admin:access", description="Acceso a panel admin")

        db.session.add_all([perm_create, perm_manage, perm_admin])
        db.session.commit()

        # --- 2. Crear Roles y Asignar Permisos ---
        # Administrador: Acceso total (incluye app:manage para CRUD)
        admin_role = Role(
            name="Administrator",
            permissions=[perm_create, perm_manage, perm_admin],
        )

        # Rol Developer: Solo permiso de creación
        dev_role = Role(name="Desarrollador", permissions=[perm_create])
        db.session.add_all([admin_role, dev_role])
        db.session.commit()

        # --- 3. Crear Usuarios ---
        temp_user = User()
        temp_user.set_password("x")
        password_hash_val = temp_user.password_hash

        admin_user = User(
            username="admin_user",
            email="admin@test.com",
            password_hash=password_hash_val,
            role_id=admin_role.id,
            is_active=True,
        )
        dev_user = User(
            username="dev_user",
            email="dev@test.com",
            password_hash=password_hash_val,
            role_id=dev_role.id,
            is_active=True,
        )
        db.session.add_all([admin_user, dev_user])
        db.session.commit()

        # --- 4. Devolver solo IDs y nombres de usuario ---
        return {
            "admin_id": admin_user.id,
            "admin_username": admin_user.username,
            "dev_id": dev_user.id,
            "dev_username": dev_user.username,
        }


def login(client, username):
    """Realiza la solicitud de login."""
    return client.post(
        "/login", data={"username": username, "password": "x"}, follow_redirects=True
    )


def test_crud_app_as_admin(client, app, setup_roles_and_users):
    """
    Verifica la creación, edición y eliminación de una aplicación
    usando una cuenta con el permiso 'app:manage'.
    """
    admin_data = setup_roles_and_users
    admin_username = admin_data["admin_username"]
    admin_id = admin_data["admin_id"]

    # 1. Iniciar sesión como administrador
    login(client, admin_username)

    with app.app_context():
        # --- CREAR ---
        create_url = "/new/app"
        resp_create = client.post(
            create_url,
            data={
                "nombre": "AppAdmin",
                "descripcion": "Una app de prueba",
                "tipo": "Backend",
                "stack": "Node.js",
                "framework": "Express",
                "repositorio_url": "http://repo.com/admin_app",
                "owner_id": str(admin_id),
                "tipo_entorno": "Servidor",
                # CORRECCIÓN CLAVE: Asegurarse de incluir todos los campos obligatorios
                "version_docker": "2.0.0",
            },
            follow_redirects=True,
        )

        # Debe redirigir y mostrar un mensaje de éxito. El código 200 es correcto.
        assert resp_create.status_code == 200
        # Verificar mensaje flash de éxito (si tu controlador lo usa)
        assert b"ha sido creada" in resp_create.data or b"AppAdmin" in resp_create.data

        app_obj = db.session.query(Application).filter_by(nombre="AppAdmin").first()
        assert app_obj is not None
        app_id = app_obj.id

        # --- EDITAR ---
        edit_url = f"/app/{app_id}/edit"
        resp_edit = client.post(
            edit_url,
            data={
                "nombre": "AppAdminEdited",
                "descripcion": "Desc editada",
                "tipo": app_obj.tipo,
                "stack": app_obj.stack,
                "framework": app_obj.framework,
                "repositorio_url": "http://repo.com/edited",
                "owner_id": str(admin_id),
                "tipo_entorno": app_obj.tipo_entorno,
                # CORRECCIÓN CLAVE: Asegurarse de incluir todos los campos obligatorios
                "version_docker": "3.0.0",
            },
            follow_redirects=True,
        )
        assert resp_edit.status_code == 200
        # Verificar mensaje flash de éxito
        assert b"Aplicaci\xc3\xb3n actualizada con \xc3\xa9xito" in resp_edit.data
        app_obj = db.session.get(Application, app_id)
        assert app_obj.nombre == "AppAdminEdited"
        assert app_obj.descripcion == "Desc editada"

        # --- ELIMINAR ---
        resp_delete = client.post(f"/app/{app_id}/delete", follow_redirects=True)
        assert resp_delete.status_code == 200
        assert b"Aplicaci\xc3\xb3n eliminada" in resp_delete.data

        app_obj_deleted = db.session.get(Application, app_id)
        assert app_obj_deleted is None


def test_permission_denied_for_developer(client, app, setup_roles_and_users):
    """
    Verifica que un Developer (solo 'app:create') no puede editar o eliminar.
    """
    admin_username = setup_roles_and_users["admin_username"]
    dev_username = setup_roles_and_users["dev_username"]

    with app.app_context():
        admin_id = setup_roles_and_users["admin_id"]
        dev_id = setup_roles_and_users["dev_id"]

        # 1. Crear una aplicación (como Admin, para asegurar que existe)
        login(client, admin_username)
        client.post(
            "/new/app",
            data={
                "nombre": "TestEditDenied",
                "descripcion": "App a intentar editar",
                "tipo": "Web",
                "stack": "Python",
                "framework": "Flask",
                "repositorio_url": "http://repo",
                "owner_id": str(admin_id),
                "tipo_entorno": "Servidor",
                # CORRECCIÓN CLAVE: Incluir campo obligatorio
                "version_docker": "1.0.0",
            },
            follow_redirects=False,
        )
        app_to_edit = (
            db.session.query(Application).filter_by(nombre="TestEditDenied").first()
        )

        # ESTA ASERCIÓN DEBE PASAR AHORA
        assert app_to_edit is not None
        app_id = app_to_edit.id

        # 2. Iniciar sesión como Developer
        login(client, dev_username)

        # 3. Intentar EDITAR (Debe fallar con 403)
        edit_url = f"/app/{app_id}/edit"
        resp_edit = client.post(
            edit_url,
            data={
                "nombre": "IntentandoEditar",
                "descripcion": "Desc2",
                "owner_id": str(dev_id),
                "tipo": app_to_edit.tipo,
                "stack": app_to_edit.stack,
                "framework": app_to_edit.framework,
                "repositorio_url": app_to_edit.repositorio_url,
                "tipo_entorno": app_to_edit.tipo_entorno,
                # Incluir campo obligatorio
                "version_docker": "1.0.1",
            },
            follow_redirects=False,
        )
        assert resp_edit.status_code == 403  # Acceso denegado

        # Comprobar que el nombre NO se actualizó
        app_check = db.session.get(Application, app_id)
        assert app_check.nombre == "TestEditDenied"

        # 4. Intentar ELIMINAR (Debe fallar con 403)
        resp_delete = client.post(f"/app/{app_id}/delete", follow_redirects=False)
        assert resp_delete.status_code == 403  # Acceso denegado

        # Comprobar que la aplicación sigue existiendo
        app_check_exists = db.session.get(Application, app_id)
        assert app_check_exists is not None
