"""Configurația comună a testelor (pytest o încarcă automat).

Fixture-urile de aici („app”, „client”) se primesc ca parametri în teste:
pytest le creează înainte de fiecare test și le distruge după, deci fiecare test
pornește de la o bază de date curată.
"""

import pytest

from app import create_app
from app.extensions import db
from app.models import Category, User

# Parola comună a conturilor de test.
PAROLA = "parola123"


@pytest.fixture
def app():
    """Aplicație de test cu bază de date SQLite în memorie (date fictive – N3)."""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        for nume, email, rol in [
            ("Ana Angajat", "angajat@technova.test", "angajat"),
            ("Bogdan Angajat", "angajat2@technova.test", "angajat"),
            ("Tudor Tehnician", "tehnician@technova.test", "tehnician"),
            ("Maria Manager", "manager@technova.test", "manager"),
        ]:
            user = User(nume=nume, email=email, rol=rol)
            user.seteaza_parola(PAROLA)
            db.session.add(user)
        db.session.add(Category(nume="Hardware"))
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Un „browser” de test care trimite cereri la aplicație fără a porni serverul."""
    return app.test_client()


def autentifica(client, email="angajat@technova.test", parola=PAROLA):
    """Se autentifică în aplicație cu contul dat (implicit angajatul Ana)."""
    return client.post("/login", data={"email": email, "parola": parola})
