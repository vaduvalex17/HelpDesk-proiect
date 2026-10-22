import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Aplicație de test cu bază de date SQLite în memorie (date fictive – N3)."""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
