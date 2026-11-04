"""Rutele pentru tichete: creare, listă, detaliu, preluare, atribuire, status, comentarii.

Cerințe acoperite: F2–F4, F6–F9 (vezi docs/specificatii.md).

Tiparul folosit în toate rutele care modifică date (POST):
    1. verificăm cine e utilizatorul și dacă are voie (rol / proprietar);
    2. validăm datele primite din formular;
    3. modificăm obiectele și facem ``db.session.commit()`` (salvare în baza de date);
    4. afișăm un mesaj (``flash``) și redirecționăm (tiparul Post/Redirect/Get, ca un
       refresh în browser să nu retrimită formularul).
"""

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..auth.decorators import role_required
from ..extensions import db
from ..models import PRIORITATI, URMATORUL_STATUS, Category, Comment, Ticket, User
from . import bp

# ---------------------------------------------------------------------------
# Funcții ajutătoare (nu sunt rute)
# ---------------------------------------------------------------------------


def categorii_active():
    """Returnează categoriile active, în ordine alfabetică (pentru lista din formular)."""
    return db.session.execute(
        db.select(Category).filter_by(activa=True).order_by(Category.nume)
    ).scalars().all()


def tichet_vizibil_sau_403(tichet_id):
    """Încarcă tichetul și verifică dacă utilizatorul curent are voie să-l vadă (F4).

    - tichet inexistent → 404 (Not Found);
    - angajat care încearcă să deschidă tichetul altcuiva → 403 (Acces interzis);
    - tehnicianul și managerul văd orice tichet.
    """
    tichet = db.get_or_404(Ticket, tichet_id)
    if current_user.rol == "angajat" and tichet.autor_id != current_user.id:
        abort(403)
    return tichet


def tehnicieni_activi():
    """Utilizatorii activi cărora li se poate atribui un tichet (tehnicieni și manageri)."""
    return db.session.execute(
        db.select(User)
        .filter(User.rol.in_(("tehnician", "manager")), User.activ.is_(True))
        .order_by(User.nume)
    ).scalars().all()


def poate_schimba_status(tichet):
    """Statusul îl schimbă doar managerul sau tehnicianul căruia îi este atribuit tichetul."""
    return current_user.are_rol("manager") or (
        current_user.are_rol("tehnician") and tichet.tehnician_id == current_user.id
    )


# ---------------------------------------------------------------------------
# Rute pentru toți utilizatorii autentificați
# ---------------------------------------------------------------------------


@bp.route("/new", methods=["GET", "POST"])
@login_required
def creeaza():
    """F2 – Creare tichet.

    - GET: afișează formularul gol.
    - POST: validează datele; dacă sunt corecte, salvează tichetul cu statusul „Nou”
      și duce utilizatorul pe pagina tichetului; altfel reafișează formularul cu erori.
    """
    categorii = categorii_active()
    erori = []
    if request.method == "POST":
        titlu = request.form.get("titlu", "").strip()
        descriere = request.form.get("descriere", "").strip()
        prioritate = request.form.get("prioritate", "")
        # type=int transformă textul în număr; „or 0” evită None (id-ul 0 nu există).
        categorie = db.session.get(Category, request.form.get("categorie_id", type=int) or 0)

        # Validare pe server: nu avem încredere în ce trimite browserul, chiar dacă
        # formularul HTML are deja „required”.
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
            # Prima intrare în istoric: „Nou” (status_vechi rămâne gol).
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
    """F3 – „Tichetele mele”: fiecare utilizator își vede doar tichetele deschise de el,
    cele mai noi primele."""
    tichete = db.session.execute(
        db.select(Ticket).filter_by(autor_id=current_user.id).order_by(Ticket.creat_la.desc())
    ).scalars().all()
    return render_template("tickets/list.html", tichete=tichete)


@bp.route("/<int:tichet_id>")
@login_required
def detaliu(tichet_id):
    """F4 – Pagina unui tichet: informații, comentarii, istoric și acțiunile permise rolului.

    Rolul decide ce butoane apar:
    - managerul vede formularul de atribuire (lista de tehnicieni);
    - managerul / tehnicianul responsabil vede butonul pentru statusul următor.
    """
    tichet = tichet_vizibil_sau_403(tichet_id)
    tehnicieni = []
    if current_user.are_rol("manager"):
        tehnicieni = tehnicieni_activi()
    status_urmator = None  # None → butonul de status nu se afișează
    if poate_schimba_status(tichet):
        status_urmator = URMATORUL_STATUS.get(tichet.status)
    return render_template(
        "tickets/detail.html",
        tichet=tichet,
        tehnicieni=tehnicieni,
        status_urmator=status_urmator,
    )


@bp.route("/<int:tichet_id>/comentarii", methods=["POST"])
@login_required
def comenteaza(tichet_id):
    """F9 – Adaugă un comentariu pe tichet (autorul și data se salvează automat).

    Oricine vede tichetul poate comenta; angajatul doar pe propriile tichete.
    """
    tichet = tichet_vizibil_sau_403(tichet_id)
    text = request.form.get("text", "").strip()
    if not text:
        flash("Comentariul nu poate fi gol.", "danger")
    else:
        db.session.add(Comment(tichet=tichet, autor=current_user, text=text))
        db.session.commit()
    # „#comentarii” face browserul să deruleze direct la secțiunea de comentarii.
    return redirect(url_for("tickets.detaliu", tichet_id=tichet.id) + "#comentarii")


# ---------------------------------------------------------------------------
# Rute doar pentru tehnician și manager
# ---------------------------------------------------------------------------


@bp.route("/tech")
@role_required("tehnician", "manager")
def panou_tehnician():
    """F6 – Panoul tehnicianului, cu două tabele:

    - tichetele noi pe care nu le-a preluat încă nimeni (cele mai vechi primele);
    - tichetele atribuite utilizatorului curent care nu sunt încă închise.
    """
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
    """F6 – Preluare: tehnicianul devine responsabil, iar tichetul trece „În lucru”.

    Dacă doi tehnicieni apasă „Preia” aproape simultan, doar primul reușește;
    al doilea primește mesajul că tichetul a fost deja preluat.
    """
    tichet = db.get_or_404(Ticket, tichet_id)
    if tichet.tehnician_id is not None or tichet.status != "Nou":
        flash(f"Tichetul #{tichet.id} a fost deja preluat.", "warning")
        return redirect(url_for("tickets.panou_tehnician"))
    tichet.tehnician = current_user
    tichet.schimba_status("În lucru", current_user)
    db.session.commit()
    flash(f"Ai preluat tichetul #{tichet.id}.", "success")
    return redirect(url_for("tickets.detaliu", tichet_id=tichet.id))


@bp.route("/<int:tichet_id>/status", methods=["POST"])
@role_required("tehnician", "manager")
def schimba_status(tichet_id):
    """F8 – Avansează tichetul cu o singură etapă; schimbarea rămâne în istoric.

    Se acceptă doar tranziția din URMATORUL_STATUS (ex. din „În lucru” doar în „Rezolvat”),
    deci nu se pot sări etape și nu se poate merge înapoi.
    """
    tichet = db.get_or_404(Ticket, tichet_id)
    if not poate_schimba_status(tichet):
        abort(403)
    status_nou = request.form.get("status", "")
    if URMATORUL_STATUS.get(tichet.status) != status_nou:
        flash("Tranziție de status invalidă.", "danger")
    else:
        # Dacă managerul avansează un tichet neatribuit, devine el responsabil.
        if tichet.tehnician is None:
            tichet.tehnician = current_user
        tichet.schimba_status(status_nou, current_user)
        db.session.commit()
        flash(f"Tichetul #{tichet.id} este acum „{status_nou}”.", "success")
    return redirect(url_for("tickets.detaliu", tichet_id=tichet.id))


# ---------------------------------------------------------------------------
# Rute doar pentru manager
# ---------------------------------------------------------------------------


@bp.route("/<int:tichet_id>/atribuie", methods=["POST"])
@role_required("manager")
def atribuie(tichet_id):
    """F7 – Managerul atribuie (sau reatribuie) orice tichet unui tehnician activ.

    Un tichet „Nou” trece automat „În lucru”; un tichet „Închis” nu mai poate fi atribuit.
    """
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
