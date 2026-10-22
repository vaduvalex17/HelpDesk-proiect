def test_pagina_principala_raspunde(client):
    raspuns = client.get("/")
    assert raspuns.status_code == 200
    assert "HelpDesk IT" in raspuns.get_data(as_text=True)
