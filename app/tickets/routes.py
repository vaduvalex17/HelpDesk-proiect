"""Rutele pentru tichete: creare, listă, detaliu, preluare, atribuire (F2–F4, F6–F8)."""

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..auth.decorators import role_required
from ..extensions import db
from ..models import PRIORITATI, URMATORUL_STATUS, Category, Ticket, User
from . import bp


def categorii_active():
    return db.session.execute(
        db.select(Category).filter_by(activa=True).order_by(Category.nume)
    ).scalars().all()


def tehnicieni_activi():
    return db.session.execute(
        db.select(User)
        .filter(User.rol.in_(("tehnician", "manager")), User.activ.is_(True))
        .order_by(User.nume)
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
            tichet.schimba_status("Nou", current_user)
            db.session.add(tichet)
            db.session.commit()
            flash(f"Tichetul #{tichet.id} a fost creat.", "success")
            return redirect(url_for("tickets.detaliu", tichet_id=tichet.id))

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


@bp.route("/<int:tichet_id>")
@login_required
def detaliu(tichet_id):
    """F4 – Detaliu tichet: un angajat nu poate deschide tichetul altui angajat."""
    tichet = db.get_or_404(Ticket, tichet_id)
    if current_user.rol == "angajat" and tichet.autor_id != current_user.id:
        abort(403)
    tehnicieni = []
    if current_user.are_rol("manager"):
        tehnicieni = tehnicieni_activi()
    status_urmator = None
    if poate_schimba_status(tichet):
        status_urmator = URMATORUL_STATUS.get(tichet.status)
    return render_template(
        "tickets/detail.html",
        tichet=tichet,
        tehnicieni=tehnicieni,
        status_urmator=status_urmator,
    )


def poate_schimba_status(tichet):
    """Statusul îl schimbă tehnicianul responsabil sau managerul."""
    return current_user.are_rol("manager") or (
        current_user.are_rol("tehnician") and tichet.tehnician_id == current_user.id
    )


@bp.route("/tech")
@role_required("tehnician", "manager")
def panou_tehnician():
    """F6 – Panoul tehnicianului: tichetele neatribuite și tichetele mele."""
    neatribuite = db.session.execute(
        db.select(Ticket)
        .filter(Ticket.tehnician_id.is_(None), Ticket.status == "Nou")
        .order_by(Ticket.creat_la)
    ).scalars().all()
    ale_mele = db.session.execute(
        db.select(Ticket)
        .filter(Ticket.tehnician_id == current_user.id, Ticket.status != "Închis")
        .order_by(Ticket.actualizat_la.desc())
    ).scalars().all()
    return render_template("tickets/tech.html", neatribuite=neatribuite, ale_mele=ale_mele)


@bp.route("/<int:tichet_id>/preia", methods=["POST"])
@role_required("tehnician", "manager")
def preia(tichet_id):
    """F6 – Preluare: tehnicianul devine responsabil, tichetul trece „În lucru”."""
    tichet = db.get_or_404(Ticket, tichet_id)
    if tichet.tehnician_id is not None or tichet.status != "Nou":
        flash(f"Tichetul #{tichet.id} a fost deja preluat.", "warning")
        return redirect(url_for("tickets.panou_tehnician"))
    tichet.tehnician = current_user
    tichet.schimba_status("În lucru", current_user)
    db.session.commit()
    flash(f"Ai preluat tichetul #{tichet.id}.", "success")
    return redirect(url_for("tickets.detaliu", tichet_id=tichet.id))


@bp.route("/<int:tichet_id>/atribuie", methods=["POST"])
@role_required("manager")
def atribuie(tichet_id):
    """F7 – Managerul atribuie orice tichet unui tehnician."""
    tichet = db.get_or_404(Ticket, tichet_id)
    tehnician = db.session.get(User, request.form.get("tehnician_id", type=int) or 0)
    if tehnician is None or not tehnician.activ or not tehnician.are_rol("tehnician", "manager"):
        flash("Alege un tehnician valid.", "danger")
    elif tichet.status == "Închis":
        flash("Un tichet închis nu mai poate fi atribuit.", "warning")
    else:
        tichet.tehnician = tehnician
        if tichet.status == "Nou":
            tichet.schimba_status("În lucru", current_user)
        db.session.commit()
        flash(f"Tichetul #{tichet.id} a fost atribuit lui {tehnician.nume}.", "success")
    return redirect(url_for("tickets.detaliu", tichet_id=tichet.id))


@bp.route("/<int:tichet_id>/status", methods=["POST"])
@role_required("tehnician", "manager")
def schimba_status(tichet_id):
    """F8 – Tichetul avansează o etapă; schimbarea rămâne în istoric."""
    tichet = db.get_or_404(Ticket, tichet_id)
    if not poate_schimba_status(tichet):
        abort(403)
    status_nou = request.form.get("status", "")
    if URMATORUL_STATUS.get(tichet.status) != status_nou:
        flash("Tranziție de status invalidă.", "danger")
    else:
        if tichet.tehnician is None:
            tichet.tehnician = current_user
        tichet.schimba_status(status_nou, current_user)
        db.session.commit()
        flash(f"Tichetul #{tichet.id} este acum „{status_nou}”.", "success")
    return redirect(url_for("tickets.detaliu", tichet_id=tichet.id))
