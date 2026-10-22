import pytest
from conftest import autentifica

from app.auth.decorators import role_required


@pytest.fixture
def app_cu_pagina_tehnica(app):
    @app.route("/doar-tehnic")
    @role_required("tehnician", "manager")
    def doar_tehnic():
        return "ok"

    return app


@pytest.mark.parametrize(
    ("email", "cod"),
    [
        ("angajat@technova.test", 403),
        ("tehnician@technova.test", 200),
        ("manager@technova.test", 200),
    ],
)
def test_acces_dupa_rol(app_cu_pagina_tehnica, email, cod):
    client = app_cu_pagina_tehnica.test_client()
    autentifica(client, email=email)
    assert client.get("/doar-tehnic").status_code == cod


def test_pagina_cu_rol_cere_autentificare(app_cu_pagina_tehnica):
    client = app_cu_pagina_tehnica.test_client()
    raspuns = client.get("/doar-tehnic")
    assert raspuns.status_code == 302
    assert "/login" in raspuns.headers["Location"]


def test_pagina_403_in_romana(app_cu_pagina_tehnica):
    client = app_cu_pagina_tehnica.test_client()
    autentifica(client)
    assert "Acces interzis" in client.get("/doar-tehnic").get_data(as_text=True)
