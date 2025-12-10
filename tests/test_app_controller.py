import os
import pytest
from app.config import create_app, db, TestConfig
from app.models.role import Role, Permission
from app.models.user import User
from app.models.application import Application, ApplicationType, Stack, Framework


@pytest.fixture(scope="function")
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def setup_roles_and_users(app):
    with app.app_context():
        perm_create = Permission(name="app:create", description="Crear aplicaciones")
        perm_read = Permission(name="app:read", description="Ver aplicaciones")
        perm_edit = Permission(name="app:edit", description="Editar aplicaciones")
        perm_delete = Permission(name="app:delete", description="Eliminar aplicaciones")
        perm_admin = Permission(name="admin:access", description="Acceso a panel admin")

        db.session.add_all([perm_create, perm_read, perm_edit, perm_delete, perm_admin])
        db.session.commit()

        admin_role = Role(
            name="Administrator",
            permissions=[perm_create, perm_read, perm_edit, perm_delete, perm_admin],
        )
        dev_role = Role(
            name="Desarrollador",
            permissions=[perm_create, perm_read],
        )
        db.session.add_all([admin_role, dev_role])
        db.session.commit()

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

        return {
            "admin_id": admin_user.id,
            "admin_username": admin_user.username,
            "dev_id": dev_user.id,
            "dev_username": dev_user.username,
        }


def login(client, username):
    return client.post(
        "/login", data={"username": username, "password": "x"}, follow_redirects=True
    )


def _crear_tipo_stack_framework():
    app_type = ApplicationType(name="Web")
    stack = Stack(name="Python")
    framework = Framework(name="Flask", stack=stack)
    db.session.add_all([app_type, stack, framework])
    db.session.commit()
    return app_type, stack, framework


def test_crud_app_as_admin(client, app, setup_roles_and_users):
    admin_data = setup_roles_and_users
    admin_username = admin_data["admin_username"]
    admin_id = admin_data["admin_id"]

    login(client, admin_username)

    with app.app_context():
        app_type, stack, framework = _crear_tipo_stack_framework()

        create_url = "/new/app"
        resp_create = client.post(
            create_url,
            data={
                "nombre": "AppAdmin",
                "descripcion": "Una app de prueba",
                "repositorio_url": "http://repo.com/admin_app",
                "version_docker": "2.0.0",
                "estado": "Activa",
                "tipo_entorno": "Producción",
                "application_type": str(app_type.id),
                "stack_obj": str(stack.id),
                "framework_obj": str(framework.id),
            },
            follow_redirects=True,
        )

        assert resp_create.status_code == 200

        app_obj = db.session.query(Application).filter_by(nombre="AppAdmin").first()
        assert app_obj is not None
        app_id = app_obj.id
        assert app_obj.owner_id == admin_id

        edit_url = f"/app/{app_id}/edit"
        resp_edit = client.post(
            edit_url,
            data={
                "nombre": "AppAdminEdited",
                "descripcion": "Desc editada",
                "repositorio_url": "http://repo.com/edited",
                "version_docker": "3.0.0",
                "estado": "En Mantenimiento",
                "tipo_entorno": "Desarrollo",
                "application_type": str(app_type.id),
                "stack_obj": str(stack.id),
                "framework_obj": str(framework.id),
            },
            follow_redirects=True,
        )

        assert resp_edit.status_code == 200

        db.session.refresh(app_obj)
        assert app_obj.nombre == "AppAdminEdited"
        assert app_obj.descripcion == "Desc editada"
        assert app_obj.version_docker == "3.0.0"
        assert app_obj.estado == "En Mantenimiento"
        assert app_obj.tipo_entorno == "Desarrollo"

        delete_url = f"/app/{app_id}/delete"
        resp_delete = client.post(delete_url, follow_redirects=True)

        assert resp_delete.status_code == 200

        assert db.session.get(Application, app_id) is None


def test_permission_denied_for_developer(client, app, setup_roles_and_users):
    admin_username = setup_roles_and_users["admin_username"]
    dev_username = setup_roles_and_users["dev_username"]

    with app.app_context():
        login(client, admin_username)
        app_type, stack, framework = _crear_tipo_stack_framework()

        create_url = "/new/app"
        client.post(
            create_url,
            data={
                "nombre": "TestEditDenied",
                "descripcion": "App a intentar editar",
                "repositorio_url": "http://repo.com/test",
                "version_docker": "1.0.0",
                "estado": "Activa",
                "tipo_entorno": "Producción",
                "application_type": str(app_type.id),
                "stack_obj": str(stack.id),
                "framework_obj": str(framework.id),
            },
            follow_redirects=True,
        )

        app_to_edit = (
            db.session.query(Application).filter_by(nombre="TestEditDenied").first()
        )
        assert app_to_edit is not None
        app_id = app_to_edit.id

    login(client, dev_username)

    edit_url = f"/app/{app_id}/edit"
    resp_edit = client.post(
        edit_url,
        data={
            "nombre": "IntentandoEditar",
            "descripcion": "Desc hack",
            "repositorio_url": "http://repo.com/hack",
            "version_docker": "1.0.1",
            "estado": "En Mantenimiento",
            "tipo_entorno": "Desarrollo",
            "application_type": str(app_type.id),
            "stack_obj": str(stack.id),
            "framework_obj": str(framework.id),
        },
        follow_redirects=False,
    )
    assert resp_edit.status_code == 403

    with app.app_context():
        app_check = db.session.get(Application, app_id)
        assert app_check.nombre == "TestEditDenied"

    delete_url = f"/app/{app_id}/delete"
    resp_delete = client.post(delete_url, follow_redirects=False)
    assert resp_delete.status_code == 403

    with app.app_context():
        assert db.session.get(Application, app_id) is not None
