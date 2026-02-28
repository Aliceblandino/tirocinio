import pandas as pd
import random
from faker import Faker

fake = Faker('it_IT')

# --------------------------
# Intestazioni generali
# --------------------------
intestazioni = [
    "Attività Didattica [COD]: FONDAMENTI DI SCIENZA DEI DATI E LABORATORIO [MA0682]",
    "Corso di Studio [COD]: INTERNET OF THINGS, BIG DATA, MACHINE LEARNING [819]",
    "Corso di Studio [COD]: INTERNET OF THINGS, BIG DATA & WEB [804]",
    "",
    "Sessioni: SESSIONE UNICA A.A. 2024/2025 [01/10/2024 - 30/04/2026]",
    "Descrizione Appello: Esame orale",
    "Tipo di Prova: Orale",
    "Prenotazione (dal-al): 21/08/2025 - 21/09/2025",
    "Date Appello: 23/09/2025 - 09:00:00 - Nessun partizionamento - Esame orale - Rizzi - Aula A023 (ex aula 47)",
    "Totale Studenti iscritti: 19",
    "",
    "Tipo Esito: Voto in trentesimi (31 = 30L, ASS = Assente, 0 = Insufficiente, RIT = Ritirato)",
    "Tipo Svolgimento Esame: P = Esame in Presenza, D = Esame a Distanza",
    ""
]

# --------------------------
# Creo DataFrame studenti
# --------------------------
num_studenti = 19
studenti = pd.DataFrame({
    "#": range(1, num_studenti + 1),
    "Matricola": [None]*num_studenti,
    "Cognome": [None]*num_studenti,
    "Nome": [None]*num_studenti,
    "Anno Freq.": ["2024/2025"]*num_studenti,
    "CFU": [6]*num_studenti,
    "Esito": [None]*num_studenti,
    "Svolgimento Esame": ["P"]*num_studenti,
    "Domande d'esame": [None]*num_studenti,
    "Data superamento": [None]*num_studenti,
    "Nota per lo studente": [None]*num_studenti,
    "CDS COD.": [819]*num_studenti,
    "AD COD.": ["MA0682"]*num_studenti,
    "Misure Compensative": [None]*num_studenti,
    "Email": [None]*num_studenti
})

# --------------------------
# Riempio dati mancanti
# --------------------------
for i in range(num_studenti):
    if not studenti.loc[i, "Matricola"]:
        studenti.loc[i, "Matricola"] = random.randint(160000, 170000)
    if not studenti.loc[i, "Cognome"]:
        studenti.loc[i, "Cognome"] = fake.last_name()
    if not studenti.loc[i, "Nome"]:
        studenti.loc[i, "Nome"] = fake.first_name()
    if not studenti.loc[i, "Esito"]:
        studenti.loc[i, "Esito"] = random.choice(list(range(18,31)) + ["30L","ASS","RIT"])
    if not studenti.loc[i, "Email"]:
        cognome = studenti.loc[i, "Cognome"].lower()
        nome = studenti.loc[i, "Nome"].lower()
        studenti.loc[i, "Email"] = f"{cognome}.{nome}@spes.uniud.it"

# --------------------------
# Scrivo file Excel con formattazione
# --------------------------
with pd.ExcelWriter("Appello_Completo_Formattato.xlsx", engine="xlsxwriter") as writer:
    workbook  = writer.book
    worksheet = workbook.add_worksheet("Appello")

    # Formati
    bold_format = workbook.add_format({'bold': True})
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border':1})
    
    # Scrivo intestazioni generali
    for r, text in enumerate(intestazioni):
        worksheet.write(r, 0, text, bold_format if text else None)

    # Riga di partenza per il DataFrame
    start_row = len(intestazioni) + 1

    # Scrivo DataFrame
    studenti.to_excel(writer, sheet_name="Appello", startrow=start_row, index=False)

    # Recupero dimensioni DataFrame
    num_rows, num_cols = studenti.shape

    # Applico formattazione alle intestazioni del DataFrame
    for col_num, value in enumerate(studenti.columns.values):
        worksheet.write(start_row, col_num, value, header_format)

    # Imposto larghezza colonne automaticamente
    for i, col in enumerate(studenti.columns):
        max_len = max(studenti[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, max_len)

print("File 'Appello_Completo_Formattato.xlsx' creato con intestazioni e formattazione!")
