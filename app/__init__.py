"""Pachetul aplicației HelpDesk IT.

Aici se află „fabrica de aplicații” (application factory) – funcția ``create_app()``.
Ea construiește obiectul Flask, îi pune configurația, conectează extensiile
(baza de date, login-ul) și înregistrează blueprint-urile (grupurile de rute).

De ce o fabrică și nu o variabilă globală ``app = Flask(...)``?
Pentru că așa putem crea mai multe aplicații cu configurații diferite – de exemplu,
testele creează o aplicație cu o bază de date în memorie, separată de cea reală.
"""

import os

from flask import Flask, redirect, render_template, url_for
from flask_login import login_required

# Importul modelelor le „înregistrează” la SQLAlchemy, ca db.create_all() să știe ce tabele să facă.
from . import models  # noqa: F401
from .extensions import db, login_manager


def create_app(config=None):
    """Creează și configurează aplicația Flask.

    Args:
        config: dicționar opțional care suprascrie configurația implicită
            (folosit de teste, ex. ``{"TESTING": True, "SQLALCHEMY_DATABASE_URI": ...}``).

    Returns:
        Aplicația Flask gata de rulat.
    """
    # instance_relative_config=True → folderul „instance/” ține fișierele locale (baza de date).
    app = Flask(__name__, instance_relative_config=True)

    # Configurația implicită. Valorile se pot schimba din variabile de mediu, fără a modifica codul.
    app.config.from_mapping(
        # Cheia cu care Flask semnează cookie-ul de sesiune (în producție se pune una secretă).
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-doar-local"),
        # Adresa bazei de date; implicit un fișier SQLite: instance/helpdesk.db
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", f"sqlite:///{os.path.join(app.instance_path, 'helpdesk.db')}"
        ),
    )
    if config:
        app.config.update(config)

    # Ne asigurăm că folderul „instance/” există, altfel SQLite nu poate crea fișierul.
    os.makedirs(app.instance_path, exist_ok=True)

    # Legăm extensiile (create o singură dată în extensions.py) de această aplicație.
    db.init_app(app)
    login_manager.init_app(app)

    # Blueprint-urile grupează rutele pe module. Le importăm aici (nu sus) ca să evităm
    # importurile circulare: rutele importă la rândul lor „db” și modelele.
    from .auth import bp as auth_bp

    app.register_blueprint(auth_bp)  # /login, /logout

    from .tickets import bp as tickets_bp

    app.register_blueprint(tickets_bp)  # /tickets/...

    @app.route("/")
    @login_required
    def index():
        """Pagina principală: trimite utilizatorul autentificat la „Tichetele mele”."""
        return redirect(url_for("tickets.lista"))

    @app.errorhandler(403)
    def acces_interzis(_eroare):
        """Afișează o pagină prietenoasă, în română, când rolul nu are acces (cod HTTP 403)."""
        return render_template("errors/403.html"), 403

    return app
