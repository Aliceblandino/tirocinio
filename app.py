# app.py
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Appello, Esito, Studente, CorsoDiStudio
from importa import importa_appello
from grafici import *  # importa tutte le funzioni dai grafici
import re
from genderize import Genderize #problema richieste limitate
import gender_guesser.detector as gender
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import click
from auth import get_user, crea_utente, crea_utente_default


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")

# ---------------- DATABASE ----------------
# file SQLite nella cartella del progetto (apribile con DBeaver)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "esami.db")
db.init_app(app)
with app.app_context():
    db.create_all()

# ---------------- LOGIN ----------------
login_manager = LoginManager(app)
login_manager.login_view = "index"  # dove mandare chi non è loggato
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
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        user = get_user(request.form.get("email", "").strip())
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember="remember" in request.form)
            next_page = request.args.get("next")
            # accetta solo percorsi interni, per evitare redirect verso altri siti
            if not next_page or not next_page.startswith("/") or next_page.startswith("//"):
                next_page = url_for("dashboard")
            return redirect(next_page)
        return render_template("index.html", error="Credenziali errate")
    return render_template("index.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logout effettuato")
    return redirect(url_for("index"))


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    files = request.files.getlist("files")
    if not files:
        return "Nessun file caricato", 400

    for file in files:
        if file.filename == "" or not allowed_file(file.filename):
            continue

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
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

    return redirect(url_for("dashboard"))

@app.route("/clear_appelli", methods=["POST"])
@login_required
def clear_appelli():
    Esito.query.delete()
    Appello.query.delete()
    db.session.commit()
    flash("Appelli rimossi")
    return redirect(url_for("dashboard"))

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

def appello_to_dict(a):
    # stessa struttura usata prima dalla sessione, così i template non cambiano
    return {
        "id": str(a.id),
        "etichetta": a.etichetta,
        "header": {
            "attivita": f"{a.corso.nome} [{a.corso.codice}]",
            "data_appello": a.data.strftime("%d/%m/%Y"),
            "tipo_prova": a.tipo_prova,
            "totale_iscritti": a.totale_iscritti,
            "aula": a.aula,
        },
    }

def lista_appelli():
    appelli = Appello.query.order_by(Appello.data).all()
    return [appello_to_dict(a) for a in appelli]

def _query_esiti(selected_appelli=None):
    query = Esito.query.join(Appello)
    if selected_appelli is not None:
        ids = [int(a) for a in selected_appelli]
        query = query.filter(Appello.id.in_(ids))
    return query.order_by(Appello.data).all()

def carica_ripetizioni(selected_appelli=None):
    rows = [
        {"matricola": e.id_studente, "appello_id": e.appello.etichetta}
        for e in _query_esiti(selected_appelli)
    ]
    return pd.DataFrame(rows, columns=["matricola", "appello_id"])

def carica_tutti_i_voti(selected_appelli=None):
    tutti_voti = []
    for e in _query_esiti(selected_appelli):
        a = e.appello
        tutti_voti.append({
            "voto": e.voto,
            "tipo": e.stato,
            "appello_id": a.etichetta,
            "materia": f"{a.corso.nome} [{a.corso.codice}]",
            "nome_raw": e.studente.nome,
            "data_appello": a.data.strftime("%d/%m/%Y"),
            "anno_freq": e.anno_freq,
            "cfu": e.cfu,
            "svolgimento": e.svolgimento
        })

    colonne = ["voto", "tipo", "appello_id", "materia", "nome_raw", "data_appello",
               "anno_freq", "cfu", "svolgimento"]
    df_all = pd.DataFrame(tutti_voti, columns=colonne)

    if df_all.empty:
        return df_all

    df_all["voto"] = pd.to_numeric(df_all["voto"], errors="coerce")

    #genre
    # normalizza nome
    df_all["Nome_norm"] = df_all["nome_raw"].apply(normalize_name)
    # gender-guesser
    df_all["Genere"] = df_all["Nome_norm"].apply(guess_gender)

    return df_all

# ---------------- DASHBOARD E STATISTICHE ----------------
#----------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    appelli = lista_appelli()
   # graph_media = None
    graph_box = None
    #graph_media_solo = None
    graph_media_globale = None
    graph_esiti = None
    graph_distribuzione_voti = None
    graph_genere = None
    graph_ripetizioni = None
    graph_ratio=None
    

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
            graph_ratio = grafico_ratio_esiti(df)


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
        graph_ripetizioni=graph_ripetizioni,
        graph_ratio=graph_ratio
    )
# ---------------- STATISTICHE GLOBALI ----------------
@app.route("/statistiche_globali_ajax", methods=["POST"])
@login_required
def statistiche_globali_ajax():
    print("\n===== AJAX DEBUG =====")
    print("POST JSON:", request.json)

    selected_stats = request.json.get("stats", [])
    selected_appelli = request.json.get("appelli", [])

    print("Selected stats:", selected_stats)
    print("Selected appelli:", selected_appelli)

    selected_appelli = [str(a) for a in selected_appelli]

    df = carica_tutti_i_voti(selected_appelli)

    print("DF filtrato appelli:", df["appello_id"].unique())
    print("DF rows:", len(df))
    print("DF columns:",len(df))
    print("DF columns:", df.columns.tolist())
    print(df.head())
    # =========================
    # CALCOLO MEDIE STORICHE
    # =========================
    df_media = (
        df[df["tipo"] == "promosso"]
        .groupby("appello_id")["voto"]
        .apply(lambda x: pd.to_numeric(x, errors="coerce").mean())
        .reset_index(name="media")
    )

    medie_storiche = df_media["media"].tolist()
    # ===== PREPARA PROMOSSI E ISCRITTI =====
    promossi, bocciati, assenti, ritirati = estrai_storico_esiti(df)

    iscritti = [
        p + b + a + r
        for p, b, a, r in zip(promossi, bocciati, assenti, ritirati)
    ]

    # ===== PREVISIONE MEDIE =====
    # n_future = int(request.json.get("n_future", 5))

    # medie_predette = forecast_exam_means(
    #     promossi,
    #     iscritti,
    #     medie_storiche,
    #     len(medie_storiche) + n_future
    # )


    print("\n=== DEBUG MEDIE STORICHE ===")
    print(df_media)
    print("Lista medie:", medie_storiche)
    results = {}

    if "voti" in selected_stats:
        print("Genero grafico: voti")
        print("Genero grafico: boxplot")
        print("Genero grafico: media")
        print("Genero grafico: esiti + cumulativa")
        results["voti"] = grafico_distribuzione_voti(df)
        results["boxplot"] = grafico_boxplot_per_appello(df)
        results["media"] = grafico_media_globale(df)
        results["esiti"] = grafico_esiti(df)
        results["cumulativa"] = grafico_distribuzione_cumulativa(df)
        results["ratio"] = grafico_ratio_esiti(df)
        results["heatmap"] = heatmap_voti(df) #???
        results["tasso"] = grafico_tasso_superamento(df)
        results["kpi"] = kpi_riepilogo(df)
    else:
        print("NON genero voti")
        print("NON genero boxplot")
        print("NON genero media")
        print("NON genero esiti")

    if "affluenza" in selected_stats:
        print("Genero grafico: genere")
        results["genere"] = grafico_genere_per_appello(df)
        print("Genero grafico: ripetizioni")
        df_rip = carica_ripetizioni(selected_appelli)
        results["ripetizioni"] = grafico_ripetizioni(df_rip)
    else:
        print("NON genero genere")
        print("NON genero ripetizioni")

    if "previsioni" in selected_stats:
        print("Genero grafico: previsioni")
        results["previsioni"] = grafico_previsione(df)
        # Previsione iscritti (grafico nuovo)
        n_future = int(request.json.get("n_future", 5))
        results["previsioneiscritti"] = grafico_previsioni_iscritti(df, n_future)
        results["previsioneesiti"] = grafico_previsione_esiti_futuri(df, n_future)
        results["previsionemedie"] = grafico_previsione_medie(df, n_future)

    else:
        print("NON genero previsioni")

    #n_future = int(request.json.get("n_future", 5))
    #results["previsioni"] = grafico_previsioni_iscritti(df, n_future)

   
        
    
    # n_future = int(request.json.get("n_future", 5))
    # results["previsioni"] = grafico_previsioni_iscritti(df, n_future)

    print("RISULTATI AJAX:", results.keys())
    print("=====================\n")

    return results

@app.route("/statistiche_globali", methods=["GET", "POST"])
@login_required
def statistiche_globali():
    appelli = lista_appelli()

    # --- DEFAULT ---
    selected_stats = [ "voti", "affluenza", "previsioni"]
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
    graph_previsione=None
    graph_heatmap=None
    graph_ratio=None
    graph_piscritti=None
    graph_previsioneesiti=None
    graph_pmedie=None
    graph_tasso=None
    kpi=None


    # --- SE CI SONO APPELLI CARICATI ---
    if appelli:

        # CARICO I VOTI DEGLI APPELLI SELEZIONATI
        df = carica_tutti_i_voti(selected_appelli)

        # SE IL DF NON È VUOTO, GENERO SOLO I GRAFICI SELEZIONATI
        if not df.empty:

            if "voti" in selected_stats:
                graph_distribuzione_voti = grafico_distribuzione_voti(df)
                graph_box = grafico_boxplot_per_appello(df)
                graph_esiti = grafico_esiti(df)
                graph_cumulativa = grafico_distribuzione_cumulativa(df)
                graph_heatmap = heatmap_voti(df) #non so se esite
                graph_media_globale = grafico_media_globale(df)
                graph_tasso = grafico_tasso_superamento(df)
                kpi = kpi_riepilogo(df)

            if "affluenza" in selected_stats:
                graph_ratio= grafico_ratio_esiti(df)
                graph_genere = grafico_genere_per_appello(df)
                df_rip = carica_ripetizioni(selected_appelli)
                graph_ripetizioni = grafico_ripetizioni(df_rip)

            if "previsioni" in selected_stats:
                graph_previsione = grafico_previsione(df)
                graph_piscritti = grafico_previsioni_iscritti(df, n_future=5)
                graph_previsioneesiti = grafico_previsione_esiti_futuri(df, n_future=5)
                graph_pmedie = grafico_previsione_medie(df, n_future=5)
        
            


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
        graph_previsione=graph_previsione,
        graph_heatmap=graph_heatmap,
        graph_ratio=graph_ratio,
        graph_piscritti=graph_piscritti,
        graph_previsioneesiti=graph_previsioneesiti,
        graph_pmedie=graph_pmedie,
        graph_tasso=graph_tasso,
        kpi=kpi
    )

# ---------------- GRAFICI PER APPELLO ----------------
@app.route("/grafici/appello/<int:appello_id>")
@login_required
def grafici_appello(appello_id):
    # il template grafici.html non esiste più: il dettaglio contiene tutti i grafici
    return redirect(url_for("dettaglio_appello", appello_id=appello_id))

# ---------------- ELIMINAZIONE APPELLO ----------------
@app.route("/delete_appello/<int:appello_id>", methods=["POST"])
@login_required
def delete_appello(appello_id):
    appello = db.session.get(Appello, appello_id)
    if not appello:
        flash("Appello non trovato")
        return redirect(url_for("dashboard"))

    db.session.delete(appello)  # gli esiti vengono eliminati in cascata
    db.session.commit()
    flash("Appello eliminato correttamente")
    return redirect(url_for("dashboard"))

# ---------------- DETTAGLIO APPELLO ----------------
@app.route("/appello/<int:appello_id>")
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    