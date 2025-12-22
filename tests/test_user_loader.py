import pytest

from app.config import create_app, db, TestConfig
from app.models.user import User
from app.models.role import Role


@pytest.fixture(scope="session")
def app():
    """
    App de pruebas usando TestConfig (DB de test, NO tu PostgreSQL real).
    """
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Cliente de pruebas para cada test."""
    return app.test_client()


def login(client, email, password="x"):
    """Helper para hacer login en los tests (nuevo login por email)."""
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


@pytest.fixture(scope="function")
def setup_user(app):
    """
    Crea un usuario sencillo con un rol básico, para probar el flujo de login
    y el user_loader de Flask-Login.
    """
    with app.app_context():
        role = Role(name="Tester")
        db.session.add(role)
        db.session.commit()

        user = User(
            username="loader_user",
            email="loader@example.com",
            role_id=role.id,
            full_name="Loader User",
            is_active=True,
        )
        user.set_password("x")
        db.session.add(user)
        db.session.commit()

        yield user

        db.session.remove()


def test_user_loader_login_flow(client, setup_user):
    """
    Verifica que el usuario puede hacer login correctamente
    y que la aplicación responde 200.
    """
    user = setup_user

    resp = login(client, user.email, "x")
    assert resp.status_code == 200, resp.data[:300]

    assert b"loader_user" in resp.data or b"Logout" in resp.data
