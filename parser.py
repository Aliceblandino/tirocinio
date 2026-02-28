# parser.py
import pandas as pd
import re
import os

def parse_appello(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    # -------------------------
    # EXCEL (XLS / XLSX)
    # -------------------------
    if ext in [".xls", ".xlsx"]:
        # df1 = tabella studenti (riga 21 → indice 20)
        df1 = pd.read_excel(
            filepath,
            skiprows=20
        )

        # df0 = header (prime 20 righe)
        df0 = pd.read_excel(
            filepath,
            nrows=20,
            header=None
        )

        header_lines = df0.astype(str).fillna("").agg(" ".join, axis=1).tolist()

    # -------------------------
    # CSV / TSV
    # -------------------------
    else:
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

    # -------------------------
    # PARSE HEADER
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
        if "FONDAMENTI" in line and "[" in line:
            header["attivita"] = line
            m = re.search(r"\[(.*?)\]", line)
            if m:
                header["ad_cod"] = m.group(1)

        elif "INTERNET OF THINGS" in line:
            header["corsi_studio"].append(line)

        elif "Sessione" in line:
            header["sessione"] = line

        elif "Descrizione Appello" in line:
            header["descrizione"] = line

        elif "Tipo di Prova" in line:
            header["tipo_prova"] = line

        elif "Prenotazione" in line:
            header["prenotazione"] = line

        elif "Date Appello" in line:
            header["data_appello"] = line

        elif "Totale Studenti" in line:
            nums = re.findall(r"\d+", line)
            if nums:
                header["totale_iscritti"] = int(nums[0])

        elif "Tipo Esito" in line:
            meta["tipo_esito"] = line

    data = header["data_appello"].split()[0] if header["data_appello"] else "ND"
    appello_id = f"{header['ad_cod']}_{data.replace('/', '')}"

    return {
        "id": appello_id,
        "header": header,
        "meta": meta,
        "df0": df0,
        "df1": df1
    }