# app.py
# Avvio dell'applicazione: configurazione, database, login e registrazione delle pagine.
# Le pagine sono divise in blueprint nella cartella routes/.
import os

import click
from flask import Flask
from flask_login import LoginManager

from auth import get_user, crea_utente, crea_utente_default
from models import db
from routes import login, dashboard, appelli, statistiche

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")

# ---------------- DATABASE ----------------
# file SQLite nella cartella del progetto (apribile con DBeaver)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "esami.db")
db.init_app(app)
with app.app_context():
    db.create_all()

# ---------------- UPLOAD ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- LOGIN ----------------
login_manager = LoginManager(app)
login_manager.login_view = "login.index"  # dove mandare chi non è loggato
login_manager.login_message = "Effettua il login per accedere a questa pagina"

crea_utente_default()

@login_manager.user_loader
def load_user(user_id):
    # Flask-Login salva in sessione solo l'id: qui lo ritrasformiamo in un User
    return get_user(user_id)

@app.cli.command("crea-utente")
@click.argument("username")
@click.password_option()
def crea_utente_command(username, password):
    """Crea (o aggiorna) un utente: flask --app app crea-utente <username>"""
    crea_utente(username, password)
    print(f"Utente '{username}' salvato")

# ---------------- PAGINE ----------------
app.register_blueprint(login.bp)
app.register_blueprint(dashboard.bp)
app.register_blueprint(appelli.bp)
app.register_blueprint(statistiche.bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
