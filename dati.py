# dati.py
# Lettura dei dati dal database e preparazione dei DataFrame per i grafici.
import re

import pandas as pd
import gender_guesser.detector as gender

from models import Appello, Esito

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
