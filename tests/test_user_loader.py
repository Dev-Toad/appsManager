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
    resp = client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303), resp.data[:300]

    with client.session_transaction() as sess:
        assert sess.get("_user_id") is not None

    return resp


@pytest.fixture(scope="function")
def setup_user(app):
    """
    Crea un usuario sencillo con un rol básico, para probar el flujo de login
    y el user_loader de Flask-Login.
    """
    with app.app_context():
        role = Role(name="Administrador", active=True)
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
    user = setup_user

    resp = login(client, user.email, "x")
    assert resp.status_code in (302, 303)

    redirected = client.get(resp.headers["Location"], follow_redirects=True)
    assert redirected.status_code == 200
