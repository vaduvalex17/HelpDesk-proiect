"""Pachetul aplicației HelpDesk IT."""

import os

from flask import Flask, render_template

from . import models  # noqa: F401  (înregistrează modelele)
from .extensions import db


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

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
