"""F5 – Roluri și permisiuni: accesul la pagini se verifică pe server (N2)."""

from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(*roluri):
    """Permite accesul doar utilizatorilor autentificați care au unul dintre roluri."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.rol not in roluri:
                abort(403)
            return view(*args, **kwargs)

        return wrapper

    return decorator
