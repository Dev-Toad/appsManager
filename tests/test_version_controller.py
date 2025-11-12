# 1. IMPORTS: Todos al inicio del archivo (Nivel Superior)
import os
from app.config import create_app, db
from app.models.role import Role
from app.models.user import User
from app.models.application import Application
from app.models.version import Version


def setup_app_context():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    return app, ctx


def create_role_user_and_app():
    role = Role(nombre="Desarrollador")
    db.session.add(role)
    db.session.commit()

    user = User(username="devv", rol_id=role.id)
    user.set_password("x")
    db.session.add(user)
    db.session.commit()

    app_obj = Application(
        nombre="AppForVersion",
        descripcion="desc",
        owner_id=user.id,
    )
    db.session.add(app_obj)
    db.session.commit()
    return role, user, app_obj


def login_test_client(client, username):
    return client.post(
        "/login",
        data={"username": username, "password": "x"},
        follow_redirects=True,
    )


def test_create_edit_delete_version():
    app, ctx = setup_app_context()
    try:
        role, user, app_obj = create_role_user_and_app()
        client = app.test_client()

        resp = login_test_client(client, user.username)
        assert resp.status_code == 200

        resp = client.post(
            f"/app/{app_obj.id}/version/new",
            data={
                "numero_version": "1.0",
                "titulo": "v1",
                "descripcion": "desc",
                "documentacion_url": "http://doc",
                "gestor_bd": "none",
                "version_gestor_bd": "",
                "dependencias": "",
                "owner_id": str(user.id),
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200

        v = Version.query.filter_by(
            aplicacion_id=app_obj.id, numero_version="1.0"
        ).first()
        assert v is not None

        resp = client.post(
            f"/version/{v.id}/edit",
            data={
                "titulo": "v1-edited",
                "descripcion": "desc2",
                "documentacion_url": "",
                "gestor_bd": "none",
                "version_gestor_bd": "",
                "dependencias": "",
                "owner_id": str(user.id),
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        v = db.session.get(Version, v.id)
        assert v.titulo == "v1-edited"

        resp = client.post(f"/version/{v.id}/delete", follow_redirects=True)
        assert resp.status_code == 200
        v = db.session.get(Version, v.id)
        assert v is None

    finally:
        db.session.remove()
        db.drop_all()
        ctx.pop()
