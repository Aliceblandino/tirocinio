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
        "totale_iscritti": None,
        "anno_accademico": None,
        "docenti": [],
        "aula": None
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

    # Corsi di laurea (E7, E8, ... → righe 6-7, colonna 4), es. "NOME CORSO [819]"
    header["corsi_studio"] = []
    for r in range(6, 9):
        cella = df0.iloc[r, 4] if df0.shape[1] > 4 else None
        m = re.match(r"(.*)\[(\d+)\]", str(cella)) if pd.notna(cella) else None
        if m:
            header["corsi_studio"].append({"codice": int(m.group(2)), "nome": m.group(1).strip()})

    # Sessione (D10 → riga indice 9), es. "SESSIONE UNICA A.A. 2024/2025 [...]"
    header["sessione"] = df0.iloc[9, 3] if pd.notna(df0.iloc[9, 3]) else None
    m = re.search(r"A\.A\. (\d{4})/\d{4}", str(header["sessione"]))
    header["anno_accademico"] = int(m.group(1)) if m else None

    # Data appello (D14 → riga indice 13, **prima colonna**)
    # formato: "23/09/2025 - 09:00:00 - Nessun partizionamento - Esame orale - Rizzi - Aula A023"
    data_str = df0.iloc[13, 3] if pd.notna(df0.iloc[13, 3]) else None
    header["docenti"] = []
    header["aula"] = None
    if data_str:
        m = re.search(r"\d{2}/\d{2}/\d{4}", str(data_str))
        header["data_appello"] = m.group(0) if m else data_str
        parti = [p.strip() for p in str(data_str).split(" - ")]
        if len(parti) >= 6:
            header["aula"] = parti[-1]
            header["docenti"] = [d.strip() for d in re.split(r"[,/]", parti[-2]) if d.strip()]

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