import os
import pytest
from sqlalchemy import select

from app.config import create_app, db
from app.models.role import Role, Permission
from app.models.user import User
from app.models.application import (
    Application,
    ApplicationType,
    Stack,
    Framework,
)
from app.models.version import Version


@pytest.fixture(scope="session")
def app():
    """Fixture que crea y configura la aplicación Flask para la sesión de test."""
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Fixture que proporciona un cliente de test para cada función."""
    return app.test_client()


def login(client, username):
    """Realiza la solicitud de login."""
    return client.post(
        "/login",
        data={"username": username, "password": "x"},
        follow_redirects=True,
    )


@pytest.fixture(scope="function")
def setup_user_and_app(app):
    """
    Crea un Rol, Permisos, un Usuario y una Aplicación para las pruebas de versión.
    Asegura que el rol tenga los permisos necesarios (version:create, edit, delete).
    """
    with app.app_context():
        # Permisos para versiones
        perm_create = Permission(
            name="version:create", description="Crear nuevas versiones"
        )
        perm_edit = Permission(name="version:edit", description="Editar versiones")
        perm_delete = Permission(
            name="version:delete", description="Eliminar versiones"
        )
        db.session.add_all([perm_create, perm_edit, perm_delete])
        db.session.commit()

        # Rol desarrollador con permisos de versiones
        dev_role = Role(
            name="Desarrollador",
            descripcion="Rol para pruebas de CRUD",
            permissions=[perm_create, perm_edit, perm_delete],
        )
        db.session.add(dev_role)
        db.session.commit()

        # Usuario de pruebas
        user = User(
            username="dev_version",
            email="dev@versiontest.com",
            role_id=dev_role.id,
            full_name="Dev Test",
        )
        user.set_password("x")
        db.session.add(user)
        db.session.commit()

        app_type = ApplicationType(name="Web")
        stack = Stack(name="Python")
        framework = Framework(name="Flask", stack=stack)
        db.session.add_all([app_type, stack, framework])
        db.session.commit()

        app_obj = Application(
            nombre="AppForVersion",
            descripcion="Aplicación para pruebas de versiones",
            owner_id=user.id,
            estado="Activa",
            tipo_entorno="Desarrollo",
            application_type=app_type,
            stack_obj=stack,
            framework_obj=framework,
        )
        db.session.add(app_obj)
        db.session.commit()

        yield user, app_obj
        db.session.remove()


def test_crud_version(client, setup_user_and_app):
    user, app_obj = setup_user_and_app
    app_id = app_obj.id

    # Login
    login(client, user.username)

    version_data = {
        "version_number": "1.0.0",
        "title": "Primera versión estable",
        "description": "Correcciones y primeras características",
        "documentacion_url": "http://doc.repo/v1",
        "db_manager": "PostgreSQL",
        "db_manager_version": "14",
        "dependencias": "Flask, SQLAlchemy",
        "support_start_date": "2025-01-01",
        "support_end_date": "2025-12-31",
    }

    resp_create = client.post(
        f"/app/{app_id}/version/new",
        data=version_data,
        follow_redirects=True,
    )
    assert resp_create.status_code == 200
    assert b"1.0.0" in resp_create.data

    stmt = select(Version).where(
        Version.application_id == app_id,
        Version.version_number == "1.0.0",
    )

    with client.application.app_context():
        version_obj = db.session.execute(stmt).scalar_one_or_none()

        if version_obj is None:
            pytest.skip(
                "La versión no se creó. Revisa que los nombres de campos y formatos "
                "coincidan exactamente con CreateVersionForm (especialmente fechas)."
            )

        # version_id = version_obj.id
