# auth.py
# Gestione utenti per Flask-Login.
# Gli utenti sono salvati in users.json con la password in forma di hash
# (mai in chiaro).
import json
import os

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = "users.json"


class User(UserMixin):
    # UserMixin fornisce is_authenticated, is_active, is_anonymous e get_id()
    def __init__(self, username, password_hash):
        self.id = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def _carica_utenti():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _salva_utenti(utenti):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(utenti, f, indent=2)


def get_user(username):
    utenti = _carica_utenti()
    if username not in utenti:
        return None
    return User(username, utenti[username])


def crea_utente(username, password):
    utenti = _carica_utenti()
    utenti[username] = generate_password_hash(password)
    _salva_utenti(utenti)


def crea_utente_default():
    # al primo avvio crea l'utente "spes" (stesse credenziali di prima)
    if not os.path.exists(USERS_FILE):
        crea_utente("spes", "spes")
