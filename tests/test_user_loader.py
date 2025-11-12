import os
from app.config import create_app, db
from app.models.user import User


def test_load_user_returns_user(monkeypatch):
    # Forzar DB en memoria
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()

    with app.app_context():
        db.create_all()

        # Crear usuario de prueba
        u = User(username="loader_test", password_hash="x", rol_id=1)
        db.session.add(u)
        db.session.commit()

        # Ahora usar load_user desde flask-login (import circular evitado en el módulo)
        from app.models.user import load_user

        loaded = load_user(u.id)
        assert loaded is not None
        assert loaded.id == u.id
        assert loaded.username == "loader_test"
