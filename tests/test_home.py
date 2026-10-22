from conftest import autentifica


def test_pagina_principala_cere_autentificare(client):
    raspuns = client.get("/")
    assert raspuns.status_code == 302
    assert "/login" in raspuns.headers["Location"]


def test_pagina_principala_dupa_login(client):
    autentifica(client)
    raspuns = client.get("/")
    assert raspuns.status_code == 200
    assert "HelpDesk IT" in raspuns.get_data(as_text=True)
