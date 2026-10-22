"""Populează baza de date cu date fictive de test (N3 – fără date personale reale).

Rulare: python seed.py
"""

from app import create_app
from app.extensions import db
from app.models import Category, User

UTILIZATORI = [
    ("Ana Popescu", "angajat@technova.test", "angajat"),
    ("Mihai Ionescu", "tehnician@technova.test", "tehnician"),
    ("Elena Dumitrescu", "manager@technova.test", "manager"),
]
CATEGORII = ["Hardware", "Software", "Rețea", "Conturi"]
PAROLA_TEST = "parola123"


def seed():
    db.drop_all()
    db.create_all()
    for nume, email, rol in UTILIZATORI:
        user = User(nume=nume, email=email, rol=rol)
        user.seteaza_parola(PAROLA_TEST)
        db.session.add(user)
    for nume in CATEGORII:
        db.session.add(Category(nume=nume))
    db.session.commit()
    print(f"{len(UTILIZATORI)} utilizatori și {len(CATEGORII)} categorii create.")
    print(f"Parola pentru toți utilizatorii de test: {PAROLA_TEST}")


if __name__ == "__main__":
    with create_app().app_context():
        seed()
