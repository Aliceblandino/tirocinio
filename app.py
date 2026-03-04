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

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return "Nessun file caricato", 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    try:
        appello = parse_appello(filepath)
    except Exception as e:
        return f"Errore nel parsing: {e}", 500

    if "appelli" not in session:
        session["appelli"] = []

    session["appelli"].append({
        "filename": file.filename,
        "id": appello["id"],
        "header": appello["header"],
        "meta": appello["meta"]
    })
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

        df_validi = df[df["Esito"].apply(lambda x: str(x).isdigit())]
        voti = df_validi["Esito"].astype(int).tolist()

        for v in voti:
            tutti_voti.append({
                "voto": v,
                "appello_id": a["id"],
                "materia": a["header"]["attivita"]
            })

    return pd.DataFrame(tutti_voti)

# ---------------- DASHBOARD E STATISTICHE ----------------

@app.route("/dashboard")
def dashboard():
    appelli = session.get("appelli", [])
    graph_media = None
    graph_box = None

    if appelli:
        df = carica_tutti_i_voti()
        if not df.empty:
            graph_media = grafico_media_totale(df)
            graph_box = grafico_boxplot_per_appello(df)

    return render_template(
        "dashboard.html",
        appelli=appelli,
        graph_media=graph_media,
        graph_box=graph_box
    )

@app.route("/statistiche_globali")
def statistiche_globali():
    df = carica_tutti_i_voti()
    if df.empty:
        flash("Nessun dato disponibile per le statistiche")
        return redirect(url_for("dashboard"))

    graph_media = grafico_media_totale(df)
    graph_box = grafico_boxplot_per_appello(df)
    return render_template("statistiche.html", graph_media=graph_media, graph_box=graph_box)

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

if __name__ == "__main__":
    app.run(debug=True)