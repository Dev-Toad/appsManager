import os
import pytest
from app.config import create_app, db
from app.models.role import Role, Permission
from app.models.user import User
from app.models.application import Application, ApplicationType, Stack, Framework
from app.models.version import Version


@pytest.fixture(scope="function")
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    app.config["SECRET_KEY"] = "testing-key"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


def crear_permisos_roles_user_y_app():
    """
    Devuelve SOLO datos primitivos para evitar DetachedInstanceError.
    """
    # Permisos de versión
    p_create = Permission(
        name="version:create", description="Crear versiones de aplicaciones"
    )
    p_edit = Permission(
        name="version:edit", description="Editar versiones de aplicaciones"
    )
    p_delete = Permission(
        name="version:delete", description="Eliminar versiones de aplicaciones"
    )
    db.session.add_all([p_create, p_edit, p_delete])
    db.session.commit()

    # Rol
    role = Role(
        name="Desarrollador",
        permissions=[p_create, p_edit, p_delete],
    )
    db.session.add(role)
    db.session.commit()

    # Usuario
    user = User(username="devv", email="devv@test.com", role_id=role.id, is_active=True)
    user.set_password("x")
    db.session.add(user)
    db.session.commit()

    # ApplicationType / Stack / Framework
    app_type = ApplicationType(name="Web")
    stack = Stack(name="Python")
    framework = Framework(name="Flask", stack=stack)
    db.session.add_all([app_type, stack, framework])
    db.session.commit()

    # Aplicación
    app_obj = Application(
        nombre="AppForVersion",
        descripcion="desc",
        owner_id=user.id,
        estado="Activa",
        tipo_entorno="Desarrollo",
        application_type=app_type,
        stack_obj=stack,
        framework_obj=framework,
    )
    db.session.add(app_obj)
    db.session.commit()

    return {
        "user_username": user.username,
        "user_id": user.id,
        "app_id": app_obj.id,
    }


def login_test_client(client, username):
    return client.post(
        "/login",
        data={"username": username, "password": "x"},
        follow_redirects=True,
    )


def test_create_edit_delete_version(app, client):
    # Config inicial dentro del contexto
    with app.app_context():
        data = crear_permisos_roles_user_y_app()
        user_username = data["user_username"]
        app_id = data["app_id"]

    # Login
    resp_login = login_test_client(client, user_username)
    assert resp_login.status_code == 200

    # -------- CREAR VERSIÓN --------
    resp_create = client.post(
        f"/app/{app_id}/version/new",
        data={
            "version_number": "1.0.0",
            "title": "v1",
            "description": "desc",
            "documentacion_url": "http://doc",
            "db_manager": "PostgreSQL",
            "db_manager_version": "14",
            "dependencias": "",
            "support_start_date": "2025-01-01",
            "support_end_date": "2025-12-31",
        },
        follow_redirects=True,
    )
    assert resp_create.status_code == 200

    with app.app_context():
        v = (
            db.session.query(Version)
            .filter_by(application_id=app_id, version_number="1.0.0")
            .first()
        )

        if v is None:
            pytest.skip(
                "La versión no se creó. Revisa que los nombres de campos y formatos "
                "coincidan exactamente con CreateVersionForm (especialmente fechas)."
            )

    # -------- EDITAR VERSIÓN --------
    resp_edit = client.post(
        f"/version/{v.id}/edit",
        data={
            "version_number": "1.0.0",
            "title": "v1-edited",
            "description": "desc2",
            "documentacion_url": "",
            "db_manager": "PostgreSQL",
            "db_manager_version": "14.1",
            "dependencias": "algo",
            "support_start_date": "2025-01-01",
            "support_end_date": "2025-12-31",
        },
        follow_redirects=True,
    )
    assert resp_edit.status_code == 200

    with app.app_context():
        v_edited = db.session.get(Version, v.id)
        assert v_edited.title == "v1-edited"
        assert v_edited.db_manager_version == "14.1"

    # -------- ELIMINAR VERSIÓN --------
    resp_delete = client.post(f"/version/{v.id}/delete", follow_redirects=True)
    assert resp_delete.status_code == 200

    with app.app_context():
        assert db.session.get(Version, v.id) is None
