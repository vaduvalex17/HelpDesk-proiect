"""Teste pentru scriptul seed.py (datele de test și datele demonstrative)."""

from app.extensions import db
from app.models import Category, Ticket, User
from seed import CATEGORII, TICHETE_DEMO, UTILIZATORI, seed


def test_seed_creeaza_utilizatori_si_categorii(app):
    seed()
    assert len(db.session.execute(db.select(User)).scalars().all()) == len(UTILIZATORI)
    assert len(db.session.execute(db.select(Category)).scalars().all()) == len(CATEGORII)
    assert db.session.execute(db.select(Ticket)).first() is None


def test_seed_demo_creeaza_tichete_cu_istoric(app):
    seed(demo=True)
    tichete = db.session.execute(db.select(Ticket).order_by(Ticket.id)).scalars().all()
    assert [t.status for t in tichete] == [demo[4] for demo in TICHETE_DEMO]
    inchis = tichete[-1]
    assert [h.status_nou for h in inchis.istoric] == ["Nou", "În lucru", "Rezolvat", "Închis"]
    assert inchis.tehnician.email == "tehnician@technova.test"
