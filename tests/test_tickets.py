from conftest import autentifica

from app.extensions import db
from app.models import Category, Ticket, User


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


def test_angajatul_nu_are_acces_la_panou(client):
    autentifica(client)
    assert client.get("/tickets/tech").status_code == 403


def test_panoul_arata_tichetele_neatribuite(app, client):
    creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client, email="tehnician@technova.test")
    pagina = client.get("/tickets/tech").get_data(as_text=True)
    assert "Laptopul nu pornește" in pagina
    assert "Preia" in pagina


def test_tehnicianul_preia_tichetul(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client, email="tehnician@technova.test")
    client.post(f"/tickets/{tichet_id}/preia")
    tichet = db.session.get(Ticket, tichet_id)
    assert tichet.status == "În lucru"
    assert tichet.tehnician.email == "tehnician@technova.test"


def test_tichetul_nu_poate_fi_preluat_de_doua_ori(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client, email="tehnician@technova.test")
    client.post(f"/tickets/{tichet_id}/preia")
    client.post("/logout")
    autentifica(client, email="manager@technova.test")
    client.post(f"/tickets/{tichet_id}/preia")
    assert db.session.get(Ticket, tichet_id).tehnician.email == "tehnician@technova.test"


def test_angajatul_nu_poate_prelua(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client)
    assert client.post(f"/tickets/{tichet_id}/preia").status_code == 403


def id_utilizator(email):
    return db.session.execute(db.select(User).filter_by(email=email)).scalar_one().id


def test_managerul_atribuie_tichetul(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client, email="manager@technova.test")
    assert "Atribuie tichetul" in client.get(f"/tickets/{tichet_id}").get_data(as_text=True)
    client.post(
        f"/tickets/{tichet_id}/atribuie",
        data={"tehnician_id": id_utilizator("tehnician@technova.test")},
    )
    tichet = db.session.get(Ticket, tichet_id)
    assert tichet.tehnician.email == "tehnician@technova.test"
    assert tichet.status == "În lucru"


def test_nu_se_poate_atribui_unui_angajat(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client, email="manager@technova.test")
    client.post(
        f"/tickets/{tichet_id}/atribuie",
        data={"tehnician_id": id_utilizator("angajat2@technova.test")},
    )
    assert db.session.get(Ticket, tichet_id).tehnician is None


def test_tehnicianul_nu_poate_atribui(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client, email="tehnician@technova.test")
    raspuns = client.post(
        f"/tickets/{tichet_id}/atribuie",
        data={"tehnician_id": id_utilizator("tehnician@technova.test")},
    )
    assert raspuns.status_code == 403


def preia_ca_tehnician(client, tichet_id):
    autentifica(client, email="tehnician@technova.test")
    client.post(f"/tickets/{tichet_id}/preia")


def test_status_avanseaza_si_se_inregistreaza_in_istoric(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    preia_ca_tehnician(client, tichet_id)
    client.post(f"/tickets/{tichet_id}/status", data={"status": "Rezolvat"})
    client.post(f"/tickets/{tichet_id}/status", data={"status": "Închis"})

    tichet = db.session.get(Ticket, tichet_id)
    assert tichet.status == "Închis"
    assert [(h.status_vechi, h.status_nou) for h in tichet.istoric] == [
        (None, "Nou"),
        ("Nou", "În lucru"),
        ("În lucru", "Rezolvat"),
        ("Rezolvat", "Închis"),
    ]
    pagina = client.get(f"/tickets/{tichet_id}").get_data(as_text=True)
    assert "Rezolvat → Închis" in pagina


def test_nu_se_pot_sari_etape(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    preia_ca_tehnician(client, tichet_id)
    client.post(f"/tickets/{tichet_id}/status", data={"status": "Închis"})
    assert db.session.get(Ticket, tichet_id).status == "În lucru"


def test_alt_tehnician_nu_schimba_statusul(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client, email="manager@technova.test")
    client.post(
        f"/tickets/{tichet_id}/atribuie",
        data={"tehnician_id": id_utilizator("manager@technova.test")},
    )
    client.post("/logout")
    autentifica(client, email="tehnician@technova.test")
    raspuns = client.post(f"/tickets/{tichet_id}/status", data={"status": "Rezolvat"})
    assert raspuns.status_code == 403


def test_angajatul_nu_schimba_statusul(app, client):
    tichet_id = creeaza_tichet_ca(client, "angajat@technova.test")
    autentifica(client)
    raspuns = client.post(f"/tickets/{tichet_id}/status", data={"status": "În lucru"})
    assert raspuns.status_code == 403
