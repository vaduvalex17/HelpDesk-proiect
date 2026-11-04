"""Modelele bazei de date (vezi diagrama ``docs/diagrame/erd.puml``).

Fiecare clasă de aici este un tabel în baza de date, iar fiecare ``db.Column`` este o coloană.
SQLAlchemy (ORM-ul) traduce automat operațiile pe obiecte în comenzi SQL.

Tabele:
    User           – utilizatorii (angajat, tehnician, manager)
    Category       – categoriile de tichete (Hardware, Software, Rețea, Conturi)
    Ticket         – tichetele de suport
    TicketHistory  – istoricul schimbărilor de status ale unui tichet (F8)
    Comment        – comentariile de pe un tichet (F9)
"""

from datetime import UTC, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager

# Valorile permise, definite o singură dată și refolosite în rute, șabloane și validare.
ROLURI = ("angajat", "tehnician", "manager")
PRIORITATI = ("Scăzută", "Medie", "Ridicată", "Critică")
STATUSURI = ("Nou", "În lucru", "Rezolvat", "Închis")
# F8: un tichet avansează doar cu o etapă: Nou → În lucru → Rezolvat → Închis.
# Dicționarul spune, pentru fiecare status, care este singurul status următor permis.
URMATORUL_STATUS = {"Nou": "În lucru", "În lucru": "Rezolvat", "Rezolvat": "Închis"}


def acum():
    """Returnează data și ora curentă în UTC (folosită ca valoare implicită pentru date)."""
    return datetime.now(UTC)


class User(UserMixin, db.Model):
    """Un utilizator al aplicației.

    ``UserMixin`` (din Flask-Login) adaugă metodele de care are nevoie login-ul
    (``is_authenticated``, ``get_id`` etc.).
    """

    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # unic: nu pot exista dubluri
    parola_hash = db.Column(db.String(255), nullable=False)  # NU parola, ci hash-ul ei (N2)
    rol = db.Column(db.String(20), nullable=False, default="angajat")  # una din ROLURI
    activ = db.Column(db.Boolean, nullable=False, default=True)  # False = cont dezactivat
    creat_la = db.Column(db.DateTime(timezone=True), nullable=False, default=acum)

    def seteaza_parola(self, parola):
        """Salvează parola ca hash (N2 – parola în clar nu ajunge niciodată în baza de date)."""
        self.parola_hash = generate_password_hash(parola)

    def verifica_parola(self, parola):
        """Verifică dacă parola introdusă corespunde hash-ului salvat. Returnează True/False."""
        return check_password_hash(self.parola_hash, parola)

    def are_rol(self, *roluri):
        """True dacă utilizatorul are unul dintre rolurile date.

        Exemplu: ``user.are_rol("tehnician", "manager")``.
        """
        return self.rol in roluri

    @property
    def is_active(self):
        """Flask-Login refuză autentificarea utilizatorilor dezactivați (F12)."""
        return self.activ

    def __repr__(self):
        """Textul afișat când printăm obiectul (util la depanare)."""
        return f"<User {self.email} ({self.rol})>"


@login_manager.user_loader
def incarca_utilizator(user_id):
    """Spune lui Flask-Login cum să găsească utilizatorul după id-ul salvat în sesiune.

    Se apelează automat la fiecare cerere; rezultatul devine ``current_user``.
    """
    return db.session.get(User, int(user_id))


class Category(db.Model):
    """O categorie de tichete (ex. Hardware). ``activa=False`` o ascunde din formular."""

    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(50), unique=True, nullable=False)
    activa = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Category {self.nume}>"


class Ticket(db.Model):
    """Un tichet de suport: problema raportată de un angajat."""

    id = db.Column(db.Integer, primary_key=True)
    titlu = db.Column(db.String(150), nullable=False)
    descriere = db.Column(db.Text, nullable=False)
    prioritate = db.Column(db.String(10), nullable=False, default="Medie")  # una din PRIORITATI
    status = db.Column(db.String(10), nullable=False, default="Nou")  # una din STATUSURI
    # Chei străine (ForeignKey) = legături către alte tabele.
    autor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # cine l-a deschis
    tehnician_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # cine îl rezolvă (poate lipsi)
    categorie_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    creat_la = db.Column(db.DateTime(timezone=True), nullable=False, default=acum)
    # onupdate=acum → se actualizează automat la fiecare modificare a tichetului.
    actualizat_la = db.Column(
        db.DateTime(timezone=True), nullable=False, default=acum, onupdate=acum
    )

    # Relațiile ne lasă să scriem ``tichet.autor.nume`` în loc să căutăm manual după id.
    # Avem două chei spre User, deci precizăm cu foreign_keys care relație folosește care cheie.
    # backref creează și relația inversă: ``user.tichete_deschise``, ``user.tichete_atribuite``.
    autor = db.relationship("User", foreign_keys=[autor_id], backref="tichete_deschise")
    tehnician = db.relationship("User", foreign_keys=[tehnician_id], backref="tichete_atribuite")
    categorie = db.relationship("Category", backref="tichete")

    # Istoricul, ordonat cronologic. cascade="all, delete-orphan" → dacă ștergem tichetul,
    # se șterg și intrările lui din istoric.
    istoric = db.relationship(
        "TicketHistory",
        back_populates="tichet",
        order_by="TicketHistory.modificat_la",
        cascade="all, delete-orphan",
    )

    # Comentariile, ordonate cronologic, șterse odată cu tichetul.
    comentarii = db.relationship(
        "Comment",
        back_populates="tichet",
        order_by="Comment.creat_la",
        cascade="all, delete-orphan",
    )

    def schimba_status(self, status_nou, utilizator):
        """Schimbă statusul și înregistrează schimbarea în istoric (F8).

        Toate schimbările de status trec prin această metodă, ca să nu uităm vreodată
        să scriem în istoric. Validarea tranziției (ex. să nu sari etape) se face în rută.

        Args:
            status_nou: statusul în care trece tichetul.
            utilizator: cine a făcut schimbarea (apare în istoric).
        """
        self.istoric.append(
            TicketHistory(status_vechi=self.status, status_nou=status_nou, utilizator=utilizator)
        )
        self.status = status_nou

    def __repr__(self):
        return f"<Ticket #{self.id} {self.status}>"


class TicketHistory(db.Model):
    """O intrare în istoricul unui tichet: cine, când, din ce status în ce status (F8)."""

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    utilizator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status_vechi = db.Column(db.String(10))  # gol la prima intrare (crearea tichetului)
    status_nou = db.Column(db.String(10), nullable=False)
    modificat_la = db.Column(db.DateTime(timezone=True), nullable=False, default=acum)

    tichet = db.relationship("Ticket", back_populates="istoric")
    utilizator = db.relationship("User")


class Comment(db.Model):
    """Un comentariu pe un tichet, cu autor și dată (F9)."""

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    creat_la = db.Column(db.DateTime(timezone=True), nullable=False, default=acum)

    tichet = db.relationship("Ticket", back_populates="comentarii")
    autor = db.relationship("User")
