# parser.py
from io import StringIO
import pandas as pd
import re
import csv

def parse_appello(file):
    """
    Parsing di un appello Esse3:
    - df0: righe di header (fino alla tabella)
    - df1: tabella studenti (da riga contenente 'Matricola' in poi)
    - Estrae informazioni principali per header e meta
    """
    content = file.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()

    # Separazione righe header e tabella
    header_lines = []
    table_lines = []
    table_started = False

    for line in lines:
        if not table_started:
            if "Matricola" in line and "Cognome" in line:
                table_started = True
                table_lines.append(line)
            else:
                if line.strip():
                    header_lines.append(line)
        else:
            if line.strip():
                table_lines.append(line)

    if not table_lines:
        raise ValueError("Il file non contiene righe della tabella")

    # df1: tabella studenti
    table_str = "\n".join(table_lines)
    try:
        df1 = pd.read_csv(
            StringIO(table_str),
            sep="\t",
            engine="python",
            quoting=csv.QUOTE_NONE,
            on_bad_lines='skip'
        )
    except Exception as e:
        raise ValueError(f"Errore parsing tabella: {e}")

    # df0: header (tutte le righe fino alla tabella)
    df0 = pd.DataFrame(header_lines, columns=["info"])

    # Parsing header e meta
    header = {
        "attivita": None,
        "ad_cod": None,
        "corsi_studio": [],
        "sessione": None,
        "descrizione": None,
        "tipo_prova": None,
        "prenotazione": None,
        "data_appello": None,
        "totale_iscritti": None
    }
    meta = {}

    for line in header_lines:
        if "FONDAMENTI" in line and "[MA" in line:
            header["attivita"] = line.strip()
            header["ad_cod"] = re.search(r"\[(.*?)\]", line).group(1)
        elif "INTERNET OF THINGS" in line:
            header["corsi_studio"].append(line.strip())
        elif line.startswith("Sessioni"):
            header["sessione"] = line.split("\t")[-1].strip()
        elif line.startswith("Descrizione Appello"):
            header["descrizione"] = line.split("\t")[-1].strip()
        elif line.startswith("Tipo di Prova"):
            header["tipo_prova"] = line.split("\t")[-1].strip()
        elif line.startswith("Prenotazione"):
            header["prenotazione"] = line.split("\t")[-1].strip()
        elif line.startswith("Date Appello"):
            header["data_appello"] = line.split("\t")[-1].strip()
        elif line.startswith("Totale Studenti"):
            try:
                header["totale_iscritti"] = int(line.split("\t")[-1].strip())
            except:
                header["totale_iscritti"] = None
        elif line.startswith("Tipo Esito"):
            meta["tipo_esito"] = line.split("\t")[-1].strip()
        elif line.startswith("Tipo Svolgimento"):
            meta["tipo_svolgimento"] = line.split("\t")[-1].strip()

    # ID appello basato sulla data
    data = header["data_appello"].split("-")[0].strip() if header["data_appello"] else "ND"
    appello_id = f"{header['ad_cod']}_{data.replace('/', '')}"  # esempio: MA0682_23092025

    return {
        "id": appello_id,
        "header": header,
        "meta": meta,
        "df0": df0,
        "df1": df1
    }