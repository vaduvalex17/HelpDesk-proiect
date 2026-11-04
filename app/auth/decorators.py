"""F5 – Roluri și permisiuni: accesul la pagini se verifică pe server (N2).

Nu ne bazăm doar pe ascunderea butoanelor din meniu: chiar dacă cineva scrie adresa
direct în browser, serverul verifică rolul și răspunde cu 403 (Acces interzis).
"""

from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(*roluri):
    """Decorator: permite accesul doar utilizatorilor autentificați care au unul dintre roluri.

    Exemplu de folosire pe o rută::

        @bp.route("/tech")
        @role_required("tehnician", "manager")
        def panou_tehnician(): ...

    - neautentificat → trimis la pagina de login (prin ``login_required``);
    - autentificat, dar cu alt rol → eroare 403.
    """

    def decorator(view):
        @wraps(view)  # păstrează numele funcției originale (Flask îl folosește la url_for)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.rol not in roluri:
                abort(403)
            return view(*args, **kwargs)

        return wrapper

    return decorator
