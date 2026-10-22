from conftest import autentifica

from app.extensions import db
from app.models import Category, Ticket


def date_tichet(**modificari):
    categorie = db.session.execute(db.select(Category)).scalars().first()
    date = {
        "titlu": "Laptopul nu pornește",
        "descriere": "Ecran negru după actualizare.",
        "prioritate": "Ridicată",
        "categorie_id": categorie.id,
    }
    date.update(modificari)
    return date


def test_creare_tichet_cere_autentificare(client):
    raspuns = client.get("/tickets/new")
    assert raspuns.status_code == 302
    assert "/login" in raspuns.headers["Location"]


def test_creare_tichet_status_nou(app, client):
    autentifica(client)
    raspuns = client.post("/tickets/new", data=date_tichet())
    assert raspuns.status_code == 302
    tichet = db.session.execute(db.select(Ticket)).scalar_one()
    assert tichet.status == "Nou"
    assert tichet.prioritate == "Ridicată"
    assert tichet.autor.email == "angajat@technova.test"


def test_creare_tichet_fara_titlu_esueaza(app, client):
    autentifica(client)
    raspuns = client.post("/tickets/new", data=date_tichet(titlu="  "))
    assert raspuns.status_code == 200
    assert "Titlul este obligatoriu" in raspuns.get_data(as_text=True)
    assert db.session.execute(db.select(Ticket)).first() is None


def test_creare_tichet_prioritate_invalida_esueaza(app, client):
    autentifica(client)
    client.post("/tickets/new", data=date_tichet(prioritate="Urgentă"))
    assert db.session.execute(db.select(Ticket)).first() is None


def test_lista_arata_doar_tichetele_mele(app, client):
    autentifica(client, email="angajat2@technova.test")
    client.post("/tickets/new", data=date_tichet(titlu="Tichetul lui Bogdan"))
    client.post("/logout")

    autentifica(client)
    client.post("/tickets/new", data=date_tichet(titlu="Tichetul Anei"))
    pagina = client.get("/tickets").get_data(as_text=True)
    assert "Tichetul Anei" in pagina
    assert "Tichetul lui Bogdan" not in pagina


def creeaza_tichet_ca(client, email):
    autentifica(client, email=email)
    raspuns = client.post("/tickets/new", data=date_tichet())
    client.post("/logout")
    return int(raspuns.headers["Location"].rsplit("/", 1)[1])


def test_dupa_creare_ajungi_pe_detaliu(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client)
    pagina = client.get(f"/tickets/{tichet_id}").get_data(as_text=True)
    assert "Laptopul nu pornește" in pagina
    assert "Ecran negru după actualizare." in pagina


def test_angajat_nu_vede_tichetul_altuia(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat2@technova.test")
    autentifica(client)
    assert client.get(f"/tickets/{tichet_id}").status_code == 403


def test_tehnicianul_vede_orice_tichet(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat2@technova.test")
    autentifica(client, email="tehnician@technova.test")
    assert client.get(f"/tickets/{tichet_id}").status_code == 200


def test_tichet_inexistent_404(client):
    autentifica(client)
    assert client.get("/tickets/999").status_code == 404
