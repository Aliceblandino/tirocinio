# routes/appelli.py
# Caricamento, eliminazione e dettaglio dei singoli appelli.
import os

from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash
from flask_login import login_required
from werkzeug.utils import secure_filename

from models import db, Appello, Esito
from importa import importa_appello
from dati import appello_to_dict, carica_tutti_i_voti
from grafici import *  # importa tutte le funzioni dai grafici

bp = Blueprint("appelli", __name__)

ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    files = request.files.getlist("files")
    if not files:
        return "Nessun file caricato", 400

    for file in files:
        if file.filename == "" or not allowed_file(file.filename):
            continue

        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
        file.save(filepath)

        try:
            importa_appello(filepath)
        except Exception as e:
            db.session.rollback()
            print("Errore importazione:", e)
            flash(f"Impossibile importare {file.filename}")
        finally:
            # i dati ora sono nel database, il file non serve più
            os.remove(filepath)

    return redirect(url_for("dashboard.dashboard"))

@bp.route("/clear_appelli", methods=["POST"])
@login_required
def clear_appelli():
    Esito.query.delete()
    Appello.query.delete()
    db.session.commit()
    flash("Appelli rimossi")
    return redirect(url_for("dashboard.dashboard"))


# ---------------- GRAFICI PER APPELLO ----------------
@bp.route("/grafici/appello/<int:appello_id>")
@login_required
def grafici_appello(appello_id):
    # il template grafici.html non esiste più: il dettaglio contiene tutti i grafici
    return redirect(url_for("appelli.dettaglio_appello", appello_id=appello_id))

# ---------------- ELIMINAZIONE APPELLO ----------------
@bp.route("/delete_appello/<int:appello_id>", methods=["POST"])
@login_required
def delete_appello(appello_id):
    appello = db.session.get(Appello, appello_id)
    if not appello:
        flash("Appello non trovato")
        return redirect(url_for("dashboard.dashboard"))

    db.session.delete(appello)  # gli esiti vengono eliminati in cascata
    db.session.commit()
    flash("Appello eliminato correttamente")
    return redirect(url_for("dashboard.dashboard"))

# ---------------- DETTAGLIO APPELLO ----------------
@bp.route("/appello/<int:appello_id>")
@login_required
def dettaglio_appello(appello_id):
    appello = db.session.get(Appello, appello_id)
    if not appello:
        return "Appello non trovato", 404

    df = carica_tutti_i_voti()
    header = appello_to_dict(appello)["header"]
    # nei grafici gli appelli sono identificati dall'etichetta (es. MA0682_23092025)
    appello_id = appello.etichetta

    grafico_distribuzione = grafico_distribuzione_appello(df, appello_id)
    grafico_boxplot = grafico_boxplot_appello(df, appello_id)
    grafico_genere = grafico_genere_uno(df, appello_id)
    grafico_esiti=grafico_esiti_appello(df, appello_id)
    grafico_radar=grafico_statistiche_radar(df, appello_id)

    grafico_donut = grafico_esiti_donut(df, appello_id)
    grafico_ecdf = grafico_ecdf_voti(df, appello_id)
    grafico_ranking = grafico_voti_ordinati(df, appello_id)
    grafico_esiti_genere = grafico_esiti_per_genere(df, appello_id)
    grafico_gauge = grafico_gauge_superamento(df, appello_id)
    grafico_media_genere = grafico_media_per_genere(df, appello_id)
    grafico_anno_freq = grafico_voti_per_anno_freq(df, appello_id)
    grafico_tasso_anno_freq = grafico_tasso_per_anno_freq(df, appello_id)
    grafico_presenza = grafico_presenza_distanza(df, appello_id)
    grafico_fasce = grafico_fasce_voto(df, appello_id)

    stats = statistiche_appello(df, appello_id)
    kpi = kpi_appello(df, appello_id)

    return render_template(
        "dettaglio_appello.html",
        appello={"header": header},
        grafico_distribuzione=grafico_distribuzione,
        grafico_boxplot=grafico_boxplot,
        grafico_genere=grafico_genere,
        grafico_esiti=grafico_esiti,
        grafico_radar=grafico_radar,
        grafico_donut=grafico_donut,
        grafico_ecdf=grafico_ecdf,
        grafico_ranking=grafico_ranking,
        grafico_esiti_genere=grafico_esiti_genere,
        grafico_gauge=grafico_gauge,
        grafico_media_genere=grafico_media_genere,
        grafico_anno_freq=grafico_anno_freq,
        grafico_tasso_anno_freq=grafico_tasso_anno_freq,
        grafico_presenza=grafico_presenza,
        grafico_fasce=grafico_fasce,

        stats=stats,
        kpi=kpi
    )
