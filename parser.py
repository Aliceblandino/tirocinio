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
            df1 = pd.read_excel(
                filepath,
                skiprows=20,
                engine='openpyxl' if ext == '.xlsx' else 'xlrd'
            )

            # df0 = prime 20 righe (header)
            df0 = pd.read_excel(
                filepath,
                nrows=20,
                header=None,
                engine='openpyxl' if ext == '.xlsx' else 'xlrd'
            )

            # Prendiamo solo le prime due colonne per le info principali
            header_lines = df0.iloc[:, :2].astype(str).fillna("").agg("\t".join, axis=1).tolist()

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

    # -------------------------
    # PARSE HEADER PULITO
    # -------------------------
    # Materia / Attività (F6 → riga indice 6, prima colonna)
    header["attivita"] = df0.iloc[6, 0] if pd.notna(df0.iloc[6, 0]) else None

    # Codice attività tra parentesi quadre
    m = re.search(r"\[(.*?)\]", header["attivita"]) if header["attivita"] else None
    header["ad_cod"] = m.group(1) if m else None

    # Tipo di prova (D12 → riga indice 11, **prima colonna**)
    header["tipo_prova"] = df0.iloc[11, 3] if pd.notna(df0.iloc[11, 3]) else None

    # Data appello (D14 → riga indice 13, **prima colonna**)
    data_str = df0.iloc[13, 3] if pd.notna(df0.iloc[13, 3]) else None
    if data_str:
        m = re.search(r"\d{2}/\d{2}/\d{4}", str(data_str))
        header["data_appello"] = m.group(0) if m else data_str

    # Totale studenti iscritti (D15 → riga indice 14, **prima colonna**)
    tot_str = df0.iloc[14, 3] if pd.notna(df0.iloc[14, 3]) else None
    if tot_str:
        nums = re.findall(r"\d+", str(tot_str))
        header["totale_iscritti"] = int(nums[0]) if nums else None

    # -------------------------
    # PARSE META (tipo esito e tipo svolgimento)
    # -------------------------
    for line in header_lines:
        if "Tipo Esito" in line:
            meta["tipo_esito"] = line.split("\t")[-1].strip()
        elif "Tipo Svolgimento" in line:
            meta["tipo_svolgimento"] = line.split("\t")[-1].strip()

    # -------------------------
    # ID appello basato sulla data
    # -------------------------
    data_id = header["data_appello"].replace("/", "") if header["data_appello"] else "ND"
    appello_id = f"{header['ad_cod']}_{data_id}"

    return {
        "id": appello_id,
        "header": header,
        "meta": meta,
        "df0": df0,
        "df1": df1
    }