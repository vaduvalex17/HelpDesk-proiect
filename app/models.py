"""Modelele bazei de date (vezi docs/diagrame/erd.puml)."""

from datetime import UTC, datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

ROLURI = ("angajat", "tehnician", "manager")
PRIORITATI = ("Scăzută", "Medie", "Ridicată", "Critică")
STATUSURI = ("Nou", "În lucru", "Rezolvat", "Închis")


def acum():
    return datetime.now(UTC)


class User(db.Model):
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

    def __repr__(self):
        return f"<User {self.email} ({self.rol})>"


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

    def __repr__(self):
        return f"<Ticket #{self.id} {self.status}>"
