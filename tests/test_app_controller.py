import os
from app.config import create_app, db
from app.models.role import Role
from app.models.user import User
from app.models.application import Application


def setup_app_context():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    return app, ctx


def create_role_and_user():
    role = Role(nombre="Desarrollador")
    db.session.add(role)
    db.session.commit()
    user = User(username="dev", rol_id=role.id)
    # set a usable password for tests
    user.set_password("x")
    db.session.add(user)
    db.session.commit()
    return role, user


def login_test_client(client, username):
    return client.post(
        "/login", data={"username": username, "password": "x"}, follow_redirects=True
    )


def test_create_edit_delete_app():
    app, ctx = setup_app_context()
    try:
        role, user = create_role_and_user()

        client = app.test_client()

        # login
        resp = login_test_client(client, user.username)
        assert resp.status_code == 200

        # Create app
        resp = client.post(
            "/new/app",
            data={
                "nombre": "MiApp",
                "descripcion": "Desc",
                "tipo": "Web",
                "stack": "Python",
                "framework": "Flask",
                "repositorio_url": "http://repo",
                "owner_id": str(user.id),
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"Aplicaci" in resp.data  # flash or template contains 'Aplicaci' text

        app_obj = Application.query.filter_by(nombre="MiApp").first()
        assert app_obj is not None

        # Edit app
        resp = client.post(
            f"/app/{app_obj.id}/edit",
            data={
                "nombre": "MiAppEdited",
                "descripcion": "Desc2",
                "owner_id": str(user.id),
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200

        app_obj = db.session.get(Application, app_obj.id)
        assert app_obj.nombre == "MiAppEdited"

        # Delete app
        resp = client.post(f"/app/{app_obj.id}/delete", follow_redirects=True)
        assert resp.status_code == 200
        app_obj = db.session.get(Application, app_obj.id)
        assert app_obj is None

    finally:
        db.session.remove()
        db.drop_all()
        ctx.pop()
