"""Pachetul aplicației HelpDesk IT."""

import os

from flask import Flask, redirect, url_for
from flask_login import login_required

from . import models  # noqa: F401  (înregistrează modelele)
from .extensions import db, login_manager


def create_app(config=None):
    """Creează și configurează aplicația Flask (application factory)."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-doar-local"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", f"sqlite:///{os.path.join(app.instance_path, 'helpdesk.db')}"
        ),
    )
    if config:
        app.config.update(config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .auth import bp as auth_bp

    app.register_blueprint(auth_bp)

    from .tickets import bp as tickets_bp

    app.register_blueprint(tickets_bp)

    @app.route("/")
    @login_required
    def index():
        return redirect(url_for("tickets.lista"))

    return app
