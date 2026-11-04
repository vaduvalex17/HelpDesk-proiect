"""F1 – Autentificare: login și logout."""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models import User
from . import bp


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Pagina de autentificare.

    - GET: afișează formularul.
    - POST: verifică emailul și parola; dacă sunt corecte, pornește sesiunea.
    """
    # Cine e deja autentificat nu mai are ce căuta pe pagina de login.
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        # Normalizăm emailul (fără spații, litere mici) ca „Ana@X.test ” să meargă la fel.
        email = request.form.get("email", "").strip().lower()
        parola = request.form.get("parola", "")
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        # Același mesaj de eroare pentru email inexistent și parolă greșită, ca să nu
        # dezvăluim ce conturi există.
        if user and user.verifica_parola(parola) and user.activ:
            login_user(user)
            # „next” = pagina pe care voia s-o deschidă înainte de a fi trimis la login.
            urmatoarea = request.args.get("next")
            # Acceptăm doar căi locale, ca să nu redirecționăm spre alte site-uri (open redirect).
            if not urmatoarea or not urmatoarea.startswith("/") or urmatoarea.startswith("//"):
                urmatoarea = url_for("index")
            return redirect(urmatoarea)
        flash("Email sau parolă greșită.", "danger")

    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Închide sesiunea. Doar prin POST, ca un simplu link să nu poată deconecta pe cineva."""
    logout_user()
    flash("Te-ai deconectat.", "info")
    return redirect(url_for("auth.login"))
