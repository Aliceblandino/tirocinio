# parser.py
import pandas as pd
import re
import os

def parse_appello(filepath):
    """
    Parsing di un appello Esse3:
    - df0: prime 20 righe (header)
    - df1: tabella studenti (riga 21 → indice 20)
    - header: Materia, Tipo di prova, Data appello, Totale iscritti
    - meta: informazioni tipo esito e tipo svolgimento
    """

    ext = os.path.splitext(filepath)[1].lower()

    # -------------------------
    # Excel XLS / XLSX
    # -------------------------
    if ext in [".xls", ".xlsx"]:
        try:
            # df1 = tabella studenti, dalla riga 21
            df1 = pd.read_excel(filepath, skiprows=20, engine='openpyxl' if ext=='.xlsx' else 'xlrd')

            # df0 = prime 20 righe (header)
            df0 = pd.read_excel(filepath, nrows=20, header=None, engine='openpyxl' if ext=='.xlsx' else 'xlrd')
            header_lines = df0.astype(str).fillna("").agg(" ".join, axis=1).tolist()

        except Exception as e:
            raise ValueError(f"Errore nella lettura del file Excel: {e}")

    # -------------------------
    # CSV / TSV / TXT
    # -------------------------
    elif ext in [".csv", ".tsv", ".txt"]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.read().splitlines()

            header_lines = lines[:20]
            table_lines = lines[20:]

            df1 = pd.read_csv(
                "\n".join(table_lines),
                sep="\t",
                engine="python",
                on_bad_lines="skip"
            )
            df0 = pd.DataFrame(header_lines, columns=["info"])

        except Exception as e:
            raise ValueError(f"Errore nella lettura del file CSV/TSV: {e}")

    else:
        raise ValueError("Formato file non supportato")

    # -------------------------
    # PARSE HEADER E META
    # -------------------------
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
        # Materia / Attività
        if "FONDAMENTI" in line and "[" in line:
            header["attivita"] = line.strip()
            m = re.search(r"\[(.*?)\]", line)
            if m:
                header["ad_cod"] = m.group(1)

        # Corsi di studio
        elif "INTERNET OF THINGS" in line:
            header["corsi_studio"].append(line.strip())

        # Sessione
        elif "Sessione" in line:
            header["sessione"] = line.split("\t")[-1].strip()

        # Descrizione appello
        elif "Descrizione Appello" in line:
            header["descrizione"] = line.split("\t")[-1].strip()

        # Tipo di prova
        elif "Tipo di Prova" in line:
            header["tipo_prova"] = line.split("\t")[-1].strip()

        # Prenotazione
        elif "Prenotazione" in line:
            header["prenotazione"] = line.split("\t")[-1].strip()

        # Date Appello → prendiamo solo la prima data
        elif "Date Appello" in line:
            date_part = line.split("\t")[-1].strip()
            # Estrai prima data nel formato gg/mm/yyyy
            m = re.search(r"\d{2}/\d{2}/\d{4}", date_part)
            header["data_appello"] = m.group(0) if m else date_part

        # Totale studenti
        elif "Totale Studenti" in line:
            nums = re.findall(r"\d+", line)
            if nums:
                header["totale_iscritti"] = int(nums[0])

        # Meta: Tipo Esito
        elif "Tipo Esito" in line:
            meta["tipo_esito"] = line.split("\t")[-1].strip()

        # Meta: Tipo Svolgimento
        elif "Tipo Svolgimento" in line:
            meta["tipo_svolgimento"] = line.split("\t")[-1].strip()

    # ID appello basato sulla data
    data_id = header["data_appello"].replace("/", "") if header["data_appello"] else "ND"
    appello_id = f"{header['ad_cod']}_{data_id}"

    return {
        "id": appello_id,
        "header": header,
        "meta": meta,
        "df0": df0,
        "df1": df1
    }