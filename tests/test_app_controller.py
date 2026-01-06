import os
import pytest
from app.config import create_app, db, TestConfig
from app.models.role import Role, Permission
from app.models.user import User
from app.models.application import Application, ApplicationType, Stack, Framework
from app.models.external_user import ExternalUser


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

        perm_create = Permission(name="app:create")
        perm_read = Permission(name="app:read")
        perm_edit = Permission(name="app:edit")
        perm_delete = Permission(name="app:delete")
        perm_admin = Permission(name="admin:access")

        db.session.add_all([perm_create, perm_read, perm_edit, perm_delete, perm_admin])
        db.session.commit()

        admin_role = Role(
            name="Administrador",
            permissions=[perm_create, perm_read, perm_edit, perm_delete, perm_admin],
        )
        dev_role = Role(
            name="Desarrollador",
            permissions=[perm_create, perm_read],
        )
        default_role = Role(name="User", permissions=[perm_read])

        db.session.add_all([admin_role, dev_role, default_role])
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
        db.session.add(admin_user)
        db.session.commit()

        dev_email = "dev@test.com"

        import hashlib
        from datetime import date, timedelta

        raw_password = "x"
        md5_password = hashlib.md5(raw_password.encode("utf-8")).hexdigest()

        ext = ExternalUser(
            admin_usuario_id=999,
            admin_tipo_id=7,
            email=dev_email,
            password=md5_password,
            nombre="Dev Externo",
            fecha_expiracion=date.today() + timedelta(days=365),
            puede_marcar=True,
        )
        db.session.add(ext)
        db.session.commit()

        return {
            "admin_id": admin_user.id,
            "admin_email": admin_user.email,
            "dev_id": ext.admin_usuario_id,
            "dev_email": dev_email,
        }


def login(client, email):
    """Login usando email (flujo tests). Falla rápido si no se loguea."""
    resp = client.post(
        "/login",
        data={"email": email, "password": "x"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303), resp.data[:300]

    with client.session_transaction() as sess:
        assert sess.get("_user_id") is not None

    return resp


def _crear_tipo_stack_framework():
    app_type = ApplicationType(name="Web")
    stack = Stack(name="Python")
    framework = Framework(name="Flask", stack=stack)
    db.session.add_all([app_type, stack, framework])
    db.session.commit()
    return app_type, stack, framework


def test_crud_app_as_admin(client, app, setup_roles_and_users):
    admin_email = setup_roles_and_users["admin_email"]
    admin_id = setup_roles_and_users["admin_id"]

    login(client, admin_email)

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
    admin_email = setup_roles_and_users["admin_email"]
    dev_email = setup_roles_and_users["dev_email"]

    with app.app_context():
        login(client, admin_email)
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

    login(client, dev_email)

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
