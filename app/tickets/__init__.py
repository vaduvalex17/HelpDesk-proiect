"""Modulul de tichete (F2–F9): blueprint-ul „tickets”.

Toate rutele de aici încep cu /tickets (datorită lui ``url_prefix``).
"""

from flask import Blueprint

bp = Blueprint("tickets", __name__, url_prefix="/tickets")

# Importăm rutele DUPĂ ce am creat „bp”, pentru că routes.py are nevoie de el.
from . import routes  # noqa: E402, F401
