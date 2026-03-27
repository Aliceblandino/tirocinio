# app.py
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from parser import parse_appello
from grafici import *  # importa tutte le funzioni dai grafici

app = Flask(__name__)
app.secret_key = "supersecret"

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("email") == "spes" and request.form.get("password") == "spes":
            return redirect(url_for("dashboard"))
        return render_template("index.html", error="Credenziali errate")
    return render_template("index.html")

from werkzeug.utils import secure_filename



@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")

    if not files:
        return "Nessun file caricato", 400

    if "appelli" not in session:
        session["appelli"] = []

    for file in files:
        if file.filename == "":
            continue

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        try:
            appello = parse_appello(filepath)
        except Exception as e:
            print("Errore parsing:", e)
            continue  # salta file problematici

        session["appelli"].append({
            "filename": file.filename,
            "filepath": filepath,
            "id": appello["id"],
            "header": appello["header"],
            "meta": appello["meta"]
        })

    # salva ultimo come corrente
    if session["appelli"]:
        session["appello_corrente"] = session["appelli"][-1]

    return redirect(url_for("dashboard"))

@app.route("/clear_appelli", methods=["POST"])
def clear_appelli():
    # svuota cartella upload
    for f in os.listdir(app.config["UPLOAD_FOLDER"]):
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], f))
    session.clear()
    flash("Appelli rimossi")
    return redirect(url_for("dashboard"))

@app.route("/grafici")
def grafici():
    appello = session.get("appello_corrente")
    if not appello:
        flash("Nessun appello caricato")
        return redirect(url_for("dashboard"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], appello["filename"])
    appello_parsed = parse_appello(filepath)
    df1 = appello_parsed["df1"]

    if "Esito" not in df1.columns:
        flash("Il file non contiene la colonna 'Esito'. Impossibile generare grafico.")
        return redirect(url_for("dashboard"))

    graphJSON = grafico_distribuzione_voti(df1)
    return render_template("grafici.html", graphJSON=graphJSON, header=appello["header"])

# ---------------- FUNZIONI AUSILIARIE ----------------
def carica_tutti_i_voti():
    appelli = session.get("appelli", [])
    tutti_voti = []

    for a in appelli:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], a["filename"])
        parsed = parse_appello(filepath)
        df = parsed["df1"]

        if "Esito" not in df.columns:
            continue

        serie = df["Esito"].astype(str).str.strip()
        serie = serie.replace("30L", 31)

        voti_num = pd.to_numeric(serie, errors="coerce")

        for i, val in enumerate(serie):
            val_str = str(val).strip().upper()
            voto_num = voti_num.iloc[i]
            if val_str == "ASS":
                tipo = "assente"
            # RITIRATO
            elif val_str == "RIT":
                tipo = "ritirato"

            # BOCCIATO (voto = 0)
            elif pd.notna(voto_num) and voto_num == 0:
                tipo = "bocciato"

            # PROMOSSO (>=18)
            elif pd.notna(voto_num) and voto_num >= 18:
                tipo = "promosso"

            # ALTRO (valori strani)
            else:
                tipo = "altro"


            tutti_voti.append({
                "voto": voto_num,
                "tipo": tipo, 
                "appello_id": a["id"],
                "materia": a["header"]["attivita"]
            })

    return pd.DataFrame(tutti_voti)

# ---------------- DASHBOARD E STATISTICHE ----------------
#----------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    appelli = session.get("appelli", [])
   # graph_media = None
    graph_box = None
    #graph_media_solo = None
    graph_media_globale = None
    graph_esiti = None
    graph_distribuzione_voti = None


    if appelli:
        df = carica_tutti_i_voti()
        if not df.empty:
            #graph_media = grafico_distribuzione_voti(df)
            graph_distribuzione_voti = grafico_distribuzione_voti(df)
            graph_box = grafico_boxplot_per_appello(df)
            #graph_media_solo = grafico_media_voti_solo(df)
            graph_media_globale = grafico_media_globale(df)
            graph_esiti = grafico_esiti(df)
            #graph_distribuzione_voti = grafico_distribuzione_voti(df)

    return render_template(
        "dashboard.html",
        appelli=appelli,
        graph_distribuzione_voti=graph_distribuzione_voti,
        #graph_media=graph_media,
        graph_box=graph_box,
        #graph_media_solo=graph_media_solo,
        graph_media_globale=graph_media_globale,
        graph_esiti=graph_esiti
    )
# ---------------- STATISTICHE GLOBALI ----------------
@app.route("/statistiche_globali")
def statistiche_globali():
    appelli = session.get("appelli", [])
   # graph_media = None
    graph_box = None
    #graph_media_solo = None
    graph_media_globale = None
    graph_esiti = None
    graph_distribuzione_voti = None


    if appelli:
        df = carica_tutti_i_voti()
        if not df.empty:
            #graph_media = grafico_distribuzione_voti(df)
            graph_distribuzione_voti = grafico_distribuzione_voti(df)
            graph_box = grafico_boxplot_per_appello(df)
            #graph_media_solo = grafico_media_voti_solo(df)
            graph_media_globale = grafico_media_globale(df)
            graph_esiti = grafico_esiti(df)
            #graph_distribuzione_voti = grafico_distribuzione_voti(df)

    return render_template(
        "statistiche.html",
        appelli=appelli,
        graph_distribuzione_voti=graph_distribuzione_voti,
        #graph_media=graph_media,
        graph_box=graph_box,
        #graph_media_solo=graph_media_solo,
        graph_media_globale=graph_media_globale,
        graph_esiti=graph_esiti
    )

# ---------------- GRAFICI PER APPELLO ----------------
@app.route("/grafici/appello/<appello_id>")
def grafici_appello(appello_id):
    appelli = session.get("appelli", [])
    appello = next((a for a in appelli if a["id"] == appello_id), None)

    if not appello:
        flash("Appello non trovato")
        return redirect(url_for("dashboard"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], appello["filename"])
    parsed = parse_appello(filepath)
    df1 = parsed["df1"]

    if "Esito" not in df1.columns:
        flash("Il file non contiene la colonna 'Esito'.")
        return redirect(url_for("dashboard"))

    graphJSON = grafico_distribuzione_voti(df1)

    return render_template("grafici.html", graphJSON=graphJSON, header=appello["header"])

# ---------------- ELIMINAZIONE APPELLO ----------------
@app.route("/delete_appello/<appello_id>", methods=["POST"])
def delete_appello(appello_id):
    appelli = session.get("appelli", [])

    # filtra via l'appello da eliminare
    appelli = [a for a in appelli if a["id"] != appello_id]

    session["appelli"] = appelli

    # opzionale: aggiorna appello corrente
    if appelli:
        session["appello_corrente"] = appelli[-1]
    else:
        session.pop("appello_corrente", None)

    flash("Appello eliminato")

    return redirect(url_for("dashboard"))

from flask import render_template, session, abort

# ---------------- DETTAGLIO APPELLO ----------------
@app.route("/appello/<appello_id>")
def dettaglio_appello(appello_id):
    df = carica_tutti_i_voti()
    df_appello = df[df["appello_id"] == appello_id]

    if df_appello.empty:
        return "Appello non trovato", 404

    appelli = session.get("appelli", [])
    appello_obj = next((a for a in appelli if a["id"] == appello_id), None)

    if not appello_obj:
        return "Appello non trovato", 404

    header = appello_obj["header"] 

    grafico_distribuzione = grafico_distribuzione_appello(df, appello_id)
    grafico_boxplot = grafico_boxplot_appello(df, appello_id)
    grafico_media = grafico_media_appello(df, appello_id)

    return render_template(
        "dettaglio_appello.html",
        appello={"header": header},
        grafico_distribuzione=grafico_distribuzione,
        grafico_boxplot=grafico_boxplot,
        grafico_media=grafico_media
    )

if __name__ == "__main__":
    app.run(debug=True)
    