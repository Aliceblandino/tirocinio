# app.py
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from parser import parse_appello
from grafici import grafico_distribuzione_voti

app = Flask(__name__)
app.secret_key = "supersecret"
 
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def leggi_file(filepath):
    if filepath.endswith(".csv"):
        return pd.read_csv(filepath, sep=";", engine="python", on_bad_lines="skip")
    elif filepath.endswith(".xls") or filepath.endswith(".xlsx"):
        return pd.read_excel(filepath)
    return None


# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("email") == "spes" and request.form.get("password") == "spes":
            return redirect(url_for("dashboard"))
        return render_template("index.html", error="Credenziali errate")
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            flash("Nessun file selezionato")
            return redirect(url_for("upload"))

        if not allowed_file(file.filename):
            flash("Formato non supportato")
            return redirect(url_for("upload"))

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        appello = parse_appello(open(filepath, "rb"))

        session["appello_corrente"] = {
            "filename": file.filename,
            "id": appello["id"],
            "header": appello["header"],
            "meta": appello["meta"]
        }

# df1 lo usi solo per grafici, non serve salvare in sessione

# df1 lo usi solo per grafici, non serve salvare in sessione

        flash("Appello caricato correttamente")
        return redirect(url_for("dashboard"))

    return render_template("upload.html")


@app.route("/dashboard")
def dashboard():
    appello = session.get("appello_corrente")
    if not appello:
        return render_template("dashboard.html", has_data=False)

    # numero iscritti preso da header
    n_studenti = appello["header"]["totale_iscritti"]

    return render_template(
        "dashboard.html",
        has_data=True,
        n_studenti=n_studenti,
        header=appello["header"]
    )


@app.route("/grafici")
def grafici():
    app.logger.debug("Entrato in grafici()")
    appello = session.get("appello_corrente")
    app.logger.debug(f"Appello in sessione: {appello}")

    if not appello:
        app.logger.warning("Nessun appello trovato nella sessione")
        flash("Nessun appello caricato")
        return redirect(url_for("dashboard"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], appello["filename"])
    app.logger.debug(f"Path file: {filepath}")

    appello_parsed = parse_appello(open(filepath, "rb"))
    df1 = appello_parsed["df1"]
    app.logger.debug(f"Colonne df1: {df1.columns.tolist()}")

    if "Esito" not in df1.columns:
        app.logger.warning("Colonna 'Esito' non trovata in df1")
        flash("Il file non contiene la colonna 'Esito'. Impossibile generare grafico.")
        return redirect(url_for("dashboard"))

    graphJSON = grafico_distribuzione_voti(df1)
    app.logger.debug("Generato graphJSON")

    return render_template(
        "grafici.html",
        graphJSON=graphJSON,
        header=appello["header"]
    )


@app.route("/clear_appelli", methods=["POST"])
def clear_appelli():
    # Svuota cartella upload
    for f in os.listdir(app.config["UPLOAD_FOLDER"]):
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], f))

    # Svuota sessione
    session.clear()
    flash("Appelli rimossi")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)