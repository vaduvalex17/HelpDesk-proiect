"""F1 – Autentificare: login și logout."""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models import User
from . import bp


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        parola = request.form.get("parola", "")
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if user and user.verifica_parola(parola) and user.activ:
            login_user(user)
            urmatoarea = request.args.get("next")
            # acceptăm doar căi locale, ca să nu redirecționăm spre alte site-uri
            if not urmatoarea or not urmatoarea.startswith("/") or urmatoarea.startswith("//"):
                urmatoarea = url_for("index")
            return redirect(urmatoarea)
        flash("Email sau parolă greșită.", "danger")

    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Te-ai deconectat.", "info")
    return redirect(url_for("auth.login"))
