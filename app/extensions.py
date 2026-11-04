"""Extensiile Flask, create o singură dată și legate de aplicație în ``create_app()``.

Le ținem într-un fișier separat ca să le poată importa oricine (modele, rute, teste)
fără importuri circulare cu ``app/__init__.py``.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# ORM-ul: ne lasă să lucrăm cu tabelele ca și cu clase Python (vezi models.py).
db = SQLAlchemy()

# Gestionează sesiunea: cine e autentificat, login_required, logout.
login_manager = LoginManager()
# Unde e trimis un utilizator neautentificat care încearcă să deschidă o pagină protejată.
login_manager.login_view = "auth.login"
# Mesajul afișat în acel caz (în română) și culoarea lui Bootstrap („warning” = galben).
login_manager.login_message = "Autentifică-te pentru a accesa pagina."
login_manager.login_message_category = "warning"
