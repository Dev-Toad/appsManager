import os
import pytest
from app.config import db, create_app, TestConfig
from app.models.user import User
from app.models.role import Role


@pytest.fixture
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        role = Role(name="Desarrollador")
        db.session.add(role)
        db.session.commit()

        user = User(username="testuser", email="test@example.com", role_id=role.id)
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


def test_login_success(app):
    """
    Verifica que el inicio de sesión con credenciales correctas sea exitoso,
    redirija y muestre contenido del dashboard.
    """
    client = app.test_client()

    resp = client.post(
        "/login",
        data={"email": "test@example.com", "password": "secret"},
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert b"testuser" in resp.data
