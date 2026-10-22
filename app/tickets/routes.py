"""Tichete: creare (F2), listă (F3)."""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import PRIORITATI, Category, Ticket
from . import bp


def categorii_active():
    return db.session.execute(
        db.select(Category).filter_by(activa=True).order_by(Category.nume)
    ).scalars().all()


@bp.route("/new", methods=["GET", "POST"])
@login_required
def creeaza():
    categorii = categorii_active()
    erori = []
    if request.method == "POST":
        titlu = request.form.get("titlu", "").strip()
        descriere = request.form.get("descriere", "").strip()
        prioritate = request.form.get("prioritate", "")
        categorie = db.session.get(Category, request.form.get("categorie_id", type=int) or 0)

        if not titlu or len(titlu) > 150:
            erori.append("Titlul este obligatoriu (maximum 150 de caractere).")
        if not descriere:
            erori.append("Descrierea este obligatorie.")
        if prioritate not in PRIORITATI:
            erori.append("Alege o prioritate validă.")
        if categorie is None or not categorie.activa:
            erori.append("Alege o categorie validă.")

        if not erori:
            tichet = Ticket(
                titlu=titlu,
                descriere=descriere,
                prioritate=prioritate,
                categorie=categorie,
                autor=current_user,
            )
            db.session.add(tichet)
            db.session.commit()
            flash(f"Tichetul #{tichet.id} a fost creat.", "success")
            return redirect(url_for("tickets.lista"))

    return render_template(
        "tickets/new.html", categorii=categorii, prioritati=PRIORITATI, erori=erori
    )


@bp.route("")
@login_required
def lista():
    """F3 – „Tichetele mele”: angajatul își vede doar propriile tichete."""
    tichete = db.session.execute(
        db.select(Ticket).filter_by(autor_id=current_user.id).order_by(Ticket.creat_la.desc())
    ).scalars().all()
    return render_template("tickets/list.html", tichete=tichete)
