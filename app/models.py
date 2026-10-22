"""Modelele bazei de date (vezi docs/diagrame/erd.puml)."""

from datetime import UTC, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager

ROLURI = ("angajat", "tehnician", "manager")
PRIORITATI = ("Scăzută", "Medie", "Ridicată", "Critică")
STATUSURI = ("Nou", "În lucru", "Rezolvat", "Închis")
# F8: un tichet avansează doar cu o etapă: Nou → În lucru → Rezolvat → Închis
URMATORUL_STATUS = {"Nou": "În lucru", "În lucru": "Rezolvat", "Rezolvat": "Închis"}


def acum():
    return datetime.now(UTC)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    parola_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="angajat")
    activ = db.Column(db.Boolean, nullable=False, default=True)
    creat_la = db.Column(db.DateTime(timezone=True), nullable=False, default=acum)

    def seteaza_parola(self, parola):
        # N2: parola se salvează doar ca hash
        self.parola_hash = generate_password_hash(parola)

    def verifica_parola(self, parola):
        return check_password_hash(self.parola_hash, parola)

    def are_rol(self, *roluri):
        return self.rol in roluri

    @property
    def is_active(self):
        # Flask-Login refuză autentificarea utilizatorilor dezactivați (F12)
        return self.activ

    def __repr__(self):
        return f"<User {self.email} ({self.rol})>"


@login_manager.user_loader
def incarca_utilizator(user_id):
    return db.session.get(User, int(user_id))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(50), unique=True, nullable=False)
    activa = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Category {self.nume}>"


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titlu = db.Column(db.String(150), nullable=False)
    descriere = db.Column(db.Text, nullable=False)
    prioritate = db.Column(db.String(10), nullable=False, default="Medie")
    status = db.Column(db.String(10), nullable=False, default="Nou")
    autor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tehnician_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    categorie_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    creat_la = db.Column(db.DateTime(timezone=True), nullable=False, default=acum)
    actualizat_la = db.Column(
        db.DateTime(timezone=True), nullable=False, default=acum, onupdate=acum
    )

    autor = db.relationship("User", foreign_keys=[autor_id], backref="tichete_deschise")
    tehnician = db.relationship("User", foreign_keys=[tehnician_id], backref="tichete_atribuite")
    categorie = db.relationship("Category", backref="tichete")

    istoric = db.relationship(
        "TicketHistory",
        back_populates="tichet",
        order_by="TicketHistory.modificat_la",
        cascade="all, delete-orphan",
    )

    comentarii = db.relationship(
        "Comment",
        back_populates="tichet",
        order_by="Comment.creat_la",
        cascade="all, delete-orphan",
    )

    def schimba_status(self, status_nou, utilizator):
        """Schimbă statusul și înregistrează schimbarea în istoric (F8)."""
        self.istoric.append(
            TicketHistory(status_vechi=self.status, status_nou=status_nou, utilizator=utilizator)
        )
        self.status = status_nou

    def __repr__(self):
        return f"<Ticket #{self.id} {self.status}>"


class TicketHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    utilizator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status_vechi = db.Column(db.String(10))
    status_nou = db.Column(db.String(10), nullable=False)
    modificat_la = db.Column(db.DateTime(timezone=True), nullable=False, default=acum)

    tichet = db.relationship("Ticket", back_populates="istoric")
    utilizator = db.relationship("User")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    creat_la = db.Column(db.DateTime(timezone=True), nullable=False, default=acum)

    tichet = db.relationship("Ticket", back_populates="comentarii")
    autor = db.relationship("User")
