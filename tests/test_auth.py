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
        role = Role(name="Administrador", active=True)
        db.session.add(role)
        db.session.commit()

        user = User(
            username="testuser",
            email="test@example.com",
            role_id=role.id,
            is_active=True,
        )
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


def test_login_success(app):
    """
    Verifica que el inicio de sesión con credenciales correctas sea exitoso.
    Para evitar depender del contenido del dashboard, validamos redirect + sesión.
    """
    client = app.test_client()

    resp = client.post(
        "/login",
        data={"email": "test@example.com", "password": "secret"},
        follow_redirects=False,
    )

    assert resp.status_code in (302, 303), resp.data[:300]

    with client.session_transaction() as sess:
        assert sess.get("_user_id") is not None
