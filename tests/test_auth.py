import os
import pytest
from app.config import db, create_app
from app.models.user import User
from app.models.role import Role

os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        # crear rol y usuario
        role = Role(nombre="Desarrollador")
        db.session.add(role)
        db.session.commit()

        user = User(username="testuser", rol_id=role.id)
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


def test_login_success(app):
    client = app.test_client()

    resp = client.post(
        "/login",
        data={"username": "testuser", "password": "secret"},
        follow_redirects=True,
    )

    assert resp.status_code == 200
    # La plantilla base contiene el título de la aplicación
    assert b"Control de Aplicaciones" in resp.data
