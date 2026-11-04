"""Populează baza de date cu date fictive de test (N3 – fără date personale reale).

Rulare:
    python seed.py           # utilizatori + categorii (bază de date „curată”)
    python seed.py --demo    # în plus, câteva tichete în diverse stadii, pentru prezentare

ATENȚIE: scriptul șterge și recreează toate tabelele, deci pierde datele existente.
"""

import sys

from app import create_app
from app.extensions import db
from app.models import Category, Comment, Ticket, User

# (nume, email, rol) – toate conturile au aceeași parolă, PAROLA_TEST.
UTILIZATORI = [
    ("Ana Popescu", "angajat@technova.test", "angajat"),
    ("Mihai Ionescu", "tehnician@technova.test", "tehnician"),
    ("Elena Dumitrescu", "manager@technova.test", "manager"),
]
CATEGORII = ["Hardware", "Software", "Rețea", "Conturi"]
PAROLA_TEST = "parola123"

# Tichete demonstrative: (titlu, descriere, categorie, prioritate, statusul la care ajung).
TICHETE_DEMO = [
    (
        "Imprimanta de la etajul 2 nu printează",
        "Apare eroarea „Paper jam”, dar nu e nicio foaie blocată.",
        "Hardware",
        "Medie",
        "Nou",
    ),
    (
        "Nu mă pot conecta la VPN",
        "De azi-dimineață clientul VPN dă eroare de autentificare.",
        "Rețea",
        "Ridicată",
        "În lucru",
    ),
    (
        "Licență Office expirată",
        "Word și Excel se deschid doar în modul de citire.",
        "Software",
        "Critică",
        "Rezolvat",
    ),
    (
        "Resetare parolă email",
        "Am uitat parola contului de email după concediu.",
        "Conturi",
        "Scăzută",
        "Închis",
    ),
]
ETAPE = ["Nou", "În lucru", "Rezolvat", "Închis"]


def seed(demo=False):
    """Recreează tabelele și adaugă datele de test.

    Args:
        demo: dacă e True, adaugă și tichetele din TICHETE_DEMO, cu istoric și un comentariu.
    """
    db.drop_all()
    db.create_all()
    useri = {}
    for nume, email, rol in UTILIZATORI:
        user = User(nume=nume, email=email, rol=rol)
        user.seteaza_parola(PAROLA_TEST)  # salvăm hash-ul, nu parola
        db.session.add(user)
        useri[rol] = user
    categorii = {}
    for nume in CATEGORII:
        categorii[nume] = Category(nume=nume)
        db.session.add(categorii[nume])

    if demo:
        adauga_tichete_demo(useri, categorii)

    db.session.commit()
    print(f"{len(UTILIZATORI)} utilizatori și {len(CATEGORII)} categorii create.")
    if demo:
        print(f"{len(TICHETE_DEMO)} tichete demonstrative create.")
    print(f"Parola pentru toți utilizatorii de test: {PAROLA_TEST}")


def adauga_tichete_demo(useri, categorii):
    """Creează tichetele demo și le avansează prin etape, exact ca în aplicație (cu istoric)."""
    angajat, tehnician = useri["angajat"], useri["tehnician"]
    for titlu, descriere, categorie, prioritate, status_final in TICHETE_DEMO:
        tichet = Ticket(
            titlu=titlu,
            descriere=descriere,
            prioritate=prioritate,
            categorie=categorii[categorie],
            autor=angajat,
        )
        tichet.schimba_status("Nou", angajat)
        # Parcurgem etapele de după „Nou” până la statusul final dorit.
        for etapa in ETAPE[1 : ETAPE.index(status_final) + 1]:
            tichet.tehnician = tehnician
            tichet.schimba_status(etapa, tehnician)
        if tichet.tehnician:
            tichet.comentarii.append(
                Comment(autor=tehnician, text="Am preluat problema, revin cu detalii.")
            )
        db.session.add(tichet)


if __name__ == "__main__":
    # create_app() + app_context(): avem nevoie de aplicație ca „db” să știe unde e baza de date.
    with create_app().app_context():
        seed(demo="--demo" in sys.argv)
