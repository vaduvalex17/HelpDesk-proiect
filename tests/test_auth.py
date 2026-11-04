"""Teste pentru F1 – autentificare și deconectare."""

from conftest import autentifica

from app.extensions import db
from app.models import User


def test_login_corect_redirectioneaza(client):
    raspuns = autentifica(client)
    assert raspuns.status_code == 302
    assert raspuns.headers["Location"] == "/"


def test_login_parola_gresita(client):
    raspuns = autentifica(client, parola="gresit")
    assert raspuns.status_code == 200
    assert "Email sau parolă greșită" in raspuns.get_data(as_text=True)


def test_utilizator_dezactivat_nu_se_poate_loga(app, client):
    user = db.session.execute(db.select(User).filter_by(email="angajat@technova.test")).scalar_one()
    user.activ = False
    db.session.commit()
    raspuns = autentifica(client)
    assert raspuns.status_code == 200


def test_logout(client):
    autentifica(client)
    client.post("/logout")
    assert client.get("/").status_code == 302


def test_next_extern_este_ignorat(client):
    raspuns = client.post(
        "/login?next=//evil.example",
        data={"email": "angajat@technova.test", "parola": "parola123"},
    )
    assert raspuns.headers["Location"] == "/"
