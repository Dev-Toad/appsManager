import os
import pytest
from app.config import create_app, db
from app.models.role import Role, Permission
from app.models.user import User
from app.models.application import Application
from app.models.version import Version
from sqlalchemy import select


@pytest.fixture(scope="session")
def app():
    """Fixture que crea y configura la aplicación Flask para la sesión de test."""
    # 1. Configurar DB en memoria
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
        perm_create = Permission(
            name="version:create", description="Crear nuevas versiones"
        )
        perm_edit = Permission(name="version:edit", description="Editar versiones")
        perm_delete = Permission(
            name="version:delete", description="Eliminar versiones"
        )
        db.session.add_all([perm_create, perm_edit, perm_delete])
        db.session.commit()

        dev_role = Role(
            name="Desarrollador",
            descripcion="Rol para pruebas de CRUD",
            permissions=[perm_create, perm_edit, perm_delete],
        )
        db.session.add(dev_role)
        db.session.commit()

        user = User(
            username="dev_version",
            email="dev@versiontest.com",
            role_id=dev_role.id,
            full_name="Dev Test",
        )
        user.set_password("x")
        db.session.add(user)
        db.session.commit()

        app_obj = Application(
            nombre="AppForVersion",
            descripcion="Aplicación para pruebas de versiones",
            owner_id=user.id,
            tipo="Web",
            stack="Python",
            framework="Flask",
            tipo_entorno="servidor",
        )
        db.session.add(app_obj)
        db.session.commit()
        yield user, app_obj
        db.session.remove()


def test_crud_version(client, setup_user_and_app):
    user, app_obj = setup_user_and_app
    app_id = app_obj.id
    with client.session_transaction():
        login(client, user.username)

    version_data = {
        "numero_version": "1.0.0",
        "titulo": "Primera versión estable",
        "descripcion": "Correcciones y primeras características",
        "documentacion_url": "http://doc.repo/v1",
        "gestor_bd": "PostgreSQL",
        "version_gestor_bd": "14",
        "dependencias": "Flask, SQLAlchemy",
        "owner_id": str(user.id),
    }

    resp_create = client.post(
        f"/app/{app_id}/version/new",
        data=version_data,
        follow_redirects=True,
    )
    assert resp_create.status_code == 200
    assert b"1.0.0" in resp_create.data

    stmt = select(Version).where(
        Version.aplicacion_id == app_id, Version.numero_version == "1.0.0"
    )
    with client.application.app_context():
        version_obj = db.session.execute(stmt).scalar_one_or_none()
        assert version_obj is not None
        version_id = version_obj.id

        edit_url = f"/version/{version_id}/edit"
        version_data_edit = version_data.copy()
        version_data_edit.update(
            {
                "titulo": "v1.0.0 - Editado",
                "descripcion": "Desc editada",
                "owner_id": str(user.id),
            }
        )

        resp_edit = client.post(
            edit_url,
            data=version_data_edit,
            follow_redirects=True,
        )
        assert resp_edit.status_code == 200
        version_obj_edited = db.session.get(Version, version_id)
        assert version_obj_edited.titulo == "v1.0.0 - Editado"
        assert version_obj_edited.descripcion == "Desc editada"
        resp_delete = client.post(
            f"/version/{version_id}/delete", follow_redirects=True
        )
        assert resp_delete.status_code == 200
        version_obj_deleted = db.session.get(Version, version_id)
        assert version_obj_deleted is None
