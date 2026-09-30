# importa.py
# Legge un file Esse3 (con parse_appello) e salva i dati nel database.
import re
from datetime import datetime

import pandas as pd

from models import db, CorsoDiLaurea, CorsoDiStudio, Docente, Appello, Studente, Esito
from parser import parse_appello


def _stato_e_voto(esito):
    """Converte la cella 'Esito' di Esse3 in (stato, voto)."""
    val = str(esito).strip().upper()
    if val == "ASS":
        return "assente", None
    if val == "RIT":
        return "ritirato", None
    if val == "30L":
        val = "31"
    voto = pd.to_numeric(val, errors="coerce")
    if pd.isna(voto):
        return "altro", None
    voto = int(voto)
    if voto == 0:
        return "bocciato", 0
    if voto >= 18:
        return "promosso", voto
    return "altro", voto


def _valore(riga, colonna):
    if colonna not in riga.index or pd.isna(riga[colonna]):
        return None
    return riga[colonna]


def importa_appello(filepath):
    """Importa un appello nel database e lo restituisce.
    Se l'appello (stesso corso e stessa data) esiste già, i suoi esiti vengono sostituiti."""
    parsed = parse_appello(filepath)
    header = parsed["header"]
    df = parsed["df1"]
    df.columns = df.columns.astype(str).str.strip()

    if not header["ad_cod"] or not header["data_appello"]:
        raise ValueError("Codice attività o data appello mancanti nel file")

    # --- Corso di laurea (il primo elencato nel file) ---
    cdl = None
    if header["corsi_studio"]:
        info = header["corsi_studio"][0]
        cdl = db.session.get(CorsoDiLaurea, info["codice"])
        if cdl is None:
            cdl = CorsoDiLaurea(id=info["codice"], nome=info["nome"],
                                is_magistrale="MAGISTRALE" in info["nome"].upper())
            db.session.add(cdl)

    # --- Corso di studio (attività didattica) ---
    corso = CorsoDiStudio.query.filter_by(codice=header["ad_cod"]).first()
    if corso is None:
        nome = re.sub(r"\s*\[.*?\]\s*$", "", header["attivita"]).strip()
        corso = CorsoDiStudio(codice=header["ad_cod"], nome=nome,
                              anno=header["anno_accademico"], corso_di_laurea=cdl)
        db.session.add(corso)

    # --- Docenti (nel file c'è solo il cognome) ---
    for cognome in header["docenti"]:
        docente = Docente.query.filter_by(cognome=cognome).first()
        if docente is None:
            docente = Docente(cognome=cognome, nome="")
            db.session.add(docente)
        if docente not in corso.docenti:
            corso.docenti.append(docente)

    # --- Appello ---
    data = datetime.strptime(header["data_appello"], "%d/%m/%Y").date()
    appello = None
    if corso.id is not None:
        appello = Appello.query.filter_by(id_corso=corso.id, data=data).first()
    if appello is None:
        appello = Appello(corso=corso, data=data)
        db.session.add(appello)
    else:
        appello.esiti.clear()  # reimport: sostituisce gli esiti
    appello.aula = header["aula"]
    appello.tipo_prova = header["tipo_prova"]
    appello.totale_iscritti = header["totale_iscritti"]

    # --- Studenti ed esiti ---
    for _, riga in df.iterrows():
        matricola = pd.to_numeric(_valore(riga, "Matricola"), errors="coerce")
        if pd.isna(matricola) or "Esito" not in df.columns:
            continue
        matricola = int(matricola)

        studente = db.session.get(Studente, matricola)
        if studente is None:
            studente = Studente(matricola=matricola)
            db.session.add(studente)
        studente.nome = _valore(riga, "Nome")
        studente.cognome = _valore(riga, "Cognome")

        stato, voto = _stato_e_voto(riga["Esito"])
        cfu = pd.to_numeric(_valore(riga, "CFU"), errors="coerce")
        appello.esiti.append(Esito(
            studente=studente,
            voto=voto,
            stato=stato,
            anno_freq=_valore(riga, "Anno Freq."),
            cfu=None if pd.isna(cfu) else int(cfu),
            svolgimento=_valore(riga, "Svolgimento Esame"),
        ))

    db.session.commit()
    return appello
