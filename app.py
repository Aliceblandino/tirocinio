# app.py
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from parser import parse_appello
from grafici import *  # importa tutte le funzioni dai grafici
import re
from genderize import Genderize #problema richieste limitate
import gender_guesser.detector as gender
from werkzeug.utils import secure_filename


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
def normalize_name(nome):
    if not isinstance(nome, str) or nome.strip() == "":
        return ""
    nome = nome.strip().split()[0]  # primo nome
    nome = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ]", "", nome)
    return nome.capitalize()

#funzione per individuazione di genere
detector=gender.Detector(case_sensitive=False)
def guess_gender(nome):
    if not nome or nome.strip() == "":
        return "?"

    g = detector.get_gender(nome)

    # gender-guesser ritorna:
    # 'male', 'female', 'mostly_male', 'mostly_female', 'andy', 'unknown'
    if g in ["male", "mostly_male"]:
        return "M"
    if g in ["female", "mostly_female"]:
        return "F"
    # 'andy' (androgino) e 'unknown' → non determinabile
    return "?"

def carica_ripetizioni(selected_appelli=None):
    appelli = session.get("appelli", [])
    rows = []

    for a in appelli:
        if selected_appelli and str(a["id"]) not in selected_appelli:
            continue

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], a["filename"])
        parsed = parse_appello(filepath)
        df = parsed["df1"]

        df.columns = df.columns.str.strip()

        if "Matricola" not in df.columns:
            continue

        for m in df["Matricola"]:
            rows.append({
                "matricola": m,
                "appello_id": str(a["id"])
            })
    return pd.DataFrame(rows)

    

def carica_tutti_i_voti():
    appelli = session.get("appelli", [])
    tutti_voti = []

    for a in appelli:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], a["filename"])
        parsed = parse_appello(filepath)
        df = parsed["df1"]

        if "Esito" not in df.columns:
            continue

        # prova a prendere il nome (adatta il nome colonna se diverso)
        col_nome = None
        for c in df.columns:
            if str(c).strip().lower() in ["nome", "studente", "cognome e nome"]:
                col_nome = c
                break

        if col_nome is None:
            df["__NOME__"] = ""
            col_nome = "__NOME__"

        serie = df["Esito"].astype(str).str.strip()
        serie = serie.replace("30L", 31)
        voti_num = pd.to_numeric(serie, errors="coerce")

        for i, val in enumerate(serie):
            val_str = str(val).strip().upper()
            voto_num = voti_num.iloc[i]
            nome_raw = df.iloc[i][col_nome]

            if val_str == "ASS":
                tipo = "assente"
            elif val_str == "RIT":
                tipo = "ritirato"
            elif pd.notna(voto_num) and voto_num == 0:
                tipo = "bocciato"
            elif pd.notna(voto_num) and voto_num >= 18:
                tipo = "promosso"
            else:
                tipo = "altro"

            tutti_voti.append({
                "voto": voto_num,
                "tipo": tipo,
                "appello_id": a["id"],
                "materia": a["header"]["attivita"],
                "nome_raw": nome_raw
            })

    df_all = pd.DataFrame(tutti_voti)

    if df_all.empty:
        return df_all

    #genre
    # normalizza nome
    df_all["Nome_norm"] = df_all["nome_raw"].apply(normalize_name)
    # gender-guesser
    df_all["Genere"] = df_all["Nome_norm"].apply(guess_gender)


    return df_all

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
    graph_genere = None
    graph_ripetizioni = None

    

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
            graph_genere = grafico_genere_per_appello(df)
            #graph_ripetizioni=grafico_ripetizioni(carica_ripetizioni())
            import json
            graph_ripetizioni = grafico_ripetizioni(carica_ripetizioni())
            parsed = json.loads(graph_ripetizioni)
            print("KEYS:", parsed.keys())
            print("DATA:", parsed.get("data"))


    return render_template(
        "dashboard.html",
        appelli=appelli,
        graph_distribuzione_voti=graph_distribuzione_voti,
        #graph_media=graph_media,
        graph_box=graph_box,
        #graph_media_solo=graph_media_solo,
        graph_media_globale=graph_media_globale,
        graph_esiti=graph_esiti,
        graph_genere=graph_genere,
        graph_ripetizioni=graph_ripetizioni
    )
# ---------------- STATISTICHE GLOBALI ----------------
@app.route("/statistiche_globali_ajax", methods=["POST"])
def statistiche_globali_ajax():
    print("\n===== AJAX DEBUG =====")
    print("POST JSON:", request.json)

    selected_stats = request.json.get("stats", [])
    selected_appelli = request.json.get("appelli", [])

    print("Selected stats:", selected_stats)
    print("Selected appelli:", selected_appelli)

    selected_appelli = [str(a) for a in selected_appelli]

    appelli = session.get("appelli", [])
    df = carica_tutti_i_voti()
    df["appello_id"] = df["appello_id"].astype(str)
    df = df[df["appello_id"].isin(selected_appelli)]

    print("DF filtrato appelli:", df["appello_id"].unique())
    print("DF rows:", len(df))
    print(df.head())

    results = {}

    if "voti" in selected_stats:
        print("Genero grafico: voti")
        results["voti"] = grafico_distribuzione_voti(df)
    else:
        print("NON genero voti")

    if "boxplot" in selected_stats:
        print("Genero grafico: boxplot")
        results["boxplot"] = grafico_boxplot_per_appello(df)
    else:
        print("NON genero boxplot")

    if "media" in selected_stats:
        print("Genero grafico: media")
        results["media"] = grafico_media_globale(df)
    else:
        print("NON genero media")

    if "esiti" in selected_stats:
        print("Genero grafico: esiti + cumulativa")
        results["esiti"] = grafico_esiti(df)
        results["cumulativa"] = grafico_distribuzione_cumulativa(df)
    else:
        print("NON genero esiti")

    if "genere" in selected_stats:
        print("Genero grafico: genere")
        results["genere"] = grafico_genere_per_appello(df)
    else:
        print("NON genero genere")

    if "ripetizioni" in selected_stats:
        print("Genero grafico: ripetizioni")
        df_rip = carica_ripetizioni(selected_appelli)
        print("Ripetizioni rows:", len(df_rip))
        results["ripetizioni"] = grafico_ripetizioni(df_rip)
    else:
        print("NON genero ripetizioni")

    print("RISULTATI AJAX:", results.keys())
    print("=====================\n")

    return results

@app.route("/statistiche_globali", methods=["GET", "POST"])
def statistiche_globali():
    appelli = session.get("appelli", [])

    # --- DEFAULT ---
    selected_stats = ["ripetizioni", "genere", "voti", "boxplot", "media", "esiti"]
    selected_appelli = [str(a["id"]) for a in appelli]  # TUTTO STRINGA

    # --- SE ARRIVA UN POST, LEGGO I FILTRI ---
    if request.method == "POST":
        selected_stats = request.form.getlist("stats")
        selected_appelli = request.form.getlist("appelli")
        selected_appelli = [str(a) for a in selected_appelli]  # normalizzo

    # --- PREPARO I GRAFICI ---
    graph_box = None
    graph_media_globale = None
    graph_esiti = None
    graph_distribuzione_voti = None
    graph_cumulativa = None
    graph_genere = None
    graph_ripetizioni = None

    # --- SE CI SONO APPELLI CARICATI ---
    if appelli:

        # CARICO TUTTI I VOTI
        df = carica_tutti_i_voti()

        # NORMALIZZO TUTTO A STRINGA
        df["appello_id"] = df["appello_id"].astype(str)

        # FILTRO GLI APPELLI SELEZIONATI
        df = df[df["appello_id"].isin(selected_appelli)]

        # SE IL DF NON È VUOTO, GENERO SOLO I GRAFICI SELEZIONATI
        if not df.empty:

            if "voti" in selected_stats:
                graph_distribuzione_voti = grafico_distribuzione_voti(df)

            if "boxplot" in selected_stats:
                graph_box = grafico_boxplot_per_appello(df)

            if "media" in selected_stats:
                graph_media_globale = grafico_media_globale(df)

            if "esiti" in selected_stats:
                graph_esiti = grafico_esiti(df)
                graph_cumulativa = grafico_distribuzione_cumulativa(df)

            if "genere" in selected_stats:
                graph_genere = grafico_genere_per_appello(df)

            if "ripetizioni" in selected_stats:
                # FILTRO ANCHE LE RIPETIZIONI
                df_rip = carica_ripetizioni(selected_appelli)
                graph_ripetizioni = grafico_ripetizioni(df_rip)

    # --- RENDER TEMPLATE ---
    return render_template(
        "statistiche.html",
        appelli=appelli,
        selected_stats=selected_stats,
        selected_appelli=selected_appelli,
        graph_distribuzione_voti=graph_distribuzione_voti,
        graph_box=graph_box,
        graph_media_globale=graph_media_globale,
        graph_esiti=graph_esiti,
        graph_cumulativa=graph_cumulativa,
        graph_genere=graph_genere,
        graph_ripetizioni=graph_ripetizioni,
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
    print("DEBUG delete_appello: appello_id URL =", appello_id)

    appelli = session.get("appelli", [])
    print("DEBUG prima, appelli in sessione:", appelli)

    # trova l'appello da eliminare (confronto sempre come stringa)
    appello_da_eliminare = next(
        (a for a in appelli if str(a.get("id")) == str(appello_id)),
        None
    )

    if not appello_da_eliminare:
        print("DEBUG: appello non trovato in sessione")
        flash("Appello non trovato")
        return redirect(url_for("dashboard"))

    # elimina file fisico se esiste
    filepath = appello_da_eliminare.get("filepath")
    print("DEBUG: filepath da eliminare:", filepath)

    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            print("DEBUG: file eliminato")
        except Exception as e:
            print("Errore eliminazione file:", e)

    # ricostruisci lista appelli senza quello eliminato
    appelli_filtrati = [a for a in appelli if str(a.get("id")) != str(appello_id)]
    print("DEBUG dopo, appelli filtrati:", appelli_filtrati)

    session["appelli"] = appelli_filtrati
    session.modified = True  # forza il salvataggio della sessione

    # aggiorna appello corrente
    if appelli_filtrati:
        session["appello_corrente"] = appelli_filtrati[-1]
    else:
        session.pop("appello_corrente", None)

    flash("Appello eliminato correttamente")
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
    grafico_genere = grafico_genere_uno(df, appello_id)

    return render_template(
        "dettaglio_appello.html",
        appello={"header": header},
        grafico_distribuzione=grafico_distribuzione,
        grafico_boxplot=grafico_boxplot,
        grafico_media=grafico_media,
        grafico_genere=grafico_genere
    )

if __name__ == "__main__":
    app.run(debug=True)
    