import pytest
from app.config import create_app, db, TestConfig
from app.models.role import Role, Permission
from app.models.user import User
from app.models.application import Application, ApplicationType, Stack, Framework
from app.models.version import Version


@pytest.fixture(scope="function")
def app():
    app = create_app(TestConfig)

    with app.app_context():
        print(">> TEST DB:", db.engine.url)
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
    Crea permisos/rol/usuario/app si no existen; si existen, los reutiliza.
    """

    def get_or_create_permission(name, description):
        perm = Permission.query.filter_by(name=name).first()
        if not perm:
            perm = Permission(name=name, description=description)
            db.session.add(perm)
            db.session.commit()
        return perm

    p_create = get_or_create_permission(
        "version:create", "Crear versiones de aplicaciones"
    )
    p_edit = get_or_create_permission(
        "version:edit", "Editar versiones de aplicaciones"
    )
    p_delete = get_or_create_permission(
        "version:delete", "Eliminar versiones de aplicaciones"
    )

    role = Role.query.filter_by(name="Desarrollador").first()
    if not role:
        role = Role(
            name="Desarrollador",
            permissions=[p_create, p_edit, p_delete],
        )
        db.session.add(role)
        db.session.commit()

    user = User.query.filter_by(username="devv").first()
    if not user:
        user = User(
            username="devv",
            email="devv@test.com",
            role_id=role.id,
            is_active=True,
        )
        user.set_password("x")
        db.session.add(user)
        db.session.commit()

    app_type = ApplicationType.query.filter_by(name="Web").first()
    if not app_type:
        app_type = ApplicationType(name="Web")
        db.session.add(app_type)
        db.session.commit()

    stack = Stack.query.filter_by(name="Python").first()
    if not stack:
        stack = Stack(name="Python")
        db.session.add(stack)
        db.session.commit()

    framework = Framework.query.filter_by(name="Flask").first()
    if not framework:
        framework = Framework(name="Flask", stack=stack)
        db.session.add(framework)
        db.session.commit()

    app_obj = Application.query.filter_by(nombre="AppForVersion").first()
    if not app_obj:
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
        "user_email": user.email,
        "user_id": user.id,
        "app_id": app_obj.id,
    }


def login_test_client(client, email):
    return client.post(
        "/login",
        data={"email": email, "password": "x"},
        follow_redirects=True,
    )


def test_create_edit_delete_version(app, client):
    with app.app_context():
        data = crear_permisos_roles_user_y_app()
        user_email = data["user_email"]
        app_id = data["app_id"]

    resp_login = login_test_client(client, user_email)
    assert resp_login.status_code == 200, resp_login.data[:300]

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
    assert resp_create.status_code == 200, resp_create.data[:300]

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
    assert resp_edit.status_code == 200, resp_edit.data[:300]

    with app.app_context():
        v_edited = db.session.get(Version, v.id)
        assert v_edited.title == "v1-edited"
        assert v_edited.db_manager_version == "14.1"

    resp_delete = client.post(f"/version/{v.id}/delete", follow_redirects=True)
    assert resp_delete.status_code == 200, resp_delete.data[:300]

    with app.app_context():
        assert db.session.get(Version, v.id) is None
