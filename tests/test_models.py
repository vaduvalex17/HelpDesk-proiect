from app.extensions import db
from app.models import Category, Ticket, User


def test_parola_se_salveaza_ca_hash(app):
    user = User(nume="Test", email="nou@technova.test", rol="angajat")
    user.seteaza_parola("secret")
    assert user.parola_hash != "secret"
    assert user.verifica_parola("secret")
    assert not user.verifica_parola("gresit")


def test_tichet_nou_are_status_nou(app):
    autor = User(nume="Test", email="nou@technova.test", rol="angajat")
    autor.seteaza_parola("secret")
    categorie = Category(nume="Software")
    tichet = Ticket(titlu="Imprimanta", descriere="Nu printează", autor=autor, categorie=categorie)
    db.session.add(tichet)
    db.session.commit()
    assert tichet.status == "Nou"
    assert tichet.prioritate == "Medie"
    assert autor.tichete_deschise == [tichet]
