from flask import Blueprint

bp = Blueprint("tickets", __name__, url_prefix="/tickets")

from . import routes  # noqa: E402, F401
