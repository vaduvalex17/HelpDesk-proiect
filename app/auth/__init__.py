"""Modulul de autentificare (F1): blueprint-ul „auth” cu rutele /login și /logout.

Un blueprint este un grup de rute care se înregistrează în aplicație în ``create_app()``.
"""

from flask import Blueprint

bp = Blueprint("auth", __name__)

# Importăm rutele DUPĂ ce am creat „bp”, pentru că routes.py are nevoie de el.
from . import routes  # noqa: E402, F401
