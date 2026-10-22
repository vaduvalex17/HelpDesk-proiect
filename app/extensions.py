"""Extensiile Flask, create o singură dată și legate de aplicație în create_app()."""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Autentifică-te pentru a accesa pagina."
login_manager.login_message_category = "warning"
