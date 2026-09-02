import pandas as pd
import random
from faker import Faker
fake = Faker('it_IT')
num_iscritti = random.randint(1, 250)
data = fake.date_between(start_date='-5y', end_date='today')


# ---------------------------------------------------------
# INTESTAZIONI (formato a due colonne, come nel file reale)
# ---------------------------------------------------------
def genera_appello(nome_file):
    intestazioni = [
        ["","","","",""],
        ["","","","",""],
        ["","","","",""],
        ["","","","",""],
        ["","","","",""],
        ["Attività Didattica [COD]"," "," ", "Corso di Studio [COD]"],
        ["FONDAMENTI DI SCIENZA DEI DATI E LABORATORIO [MA0682]"," ","" ,"INTERNET OF THINGS, BIG DATA, MACHINE LEARNING [819]"],
        ["FONDAMENTI DI SCIENZA DEI DATI E LABORATORIO [MA0682]","","","INTERNET OF THINGS, BIG DATA & WEB [804]"],
        ["", "", "", ""],
        ["Sessioni","","","SESSIONE UNICA A.A. 2024/2025 [01/10/2024 - 30/04/2026]"],
        ["Descrizione Appello","","","Esame orale", ""],
        ["Tipo di Prova","","","Orale",""],
        ["Prenotazione (dal-al)","","","21/08/2025 - 21/09/2025", ""],
        ["Date Appello","","","25/09/2025 - 09:00:00 - Nessun partizionamento - Esame orale - Rizzi - Aula A023 (ex aula 47)", ""],
        ["Totale Studenti iscritti","","",str(num_iscritti), ""],
        ["", "", "", ""],
        ["Tipo Esito","","","Voto in trentesimi (31 = 30L, ASS = Assente, 0 = Insufficiente, RIT = Ritirato)",""],
        ["Tipo Svolgimento Esame","","","P = Esame in Presenza, D = Esame a Distanza",""],
        ["", "", "", ""],
        ["Elenco Studenti Iscritti all'Appello", "", "", ""]
    ]

    # ---------------------------------------------------------
    # TABELLA STUDENTI (identica al file originale)
    # ---------------------------------------------------------
    from faker import Faker
    fake = Faker("it_IT")

    dati_studenti = []

    for i in range(1, num_iscritti + 1):
        matricola = random.randint(150000, 250000)
        cognome = fake.last_name().upper()
        nome = fake.first_name().upper()
        anno = random.choice(["2021/2022", "2022/2023", "2023/2024", "2024/2025"])
        esito = random.choice([0, 18, 19,20,21,22,23,24, 25, 26, 27, 28, 29, 30, 31, "ASS", "RIT"])
        email = fake.email() 

        dati_studenti.append([
            i, matricola, cognome, nome, anno, 6, esito, "P",
            "", "", "", 819, "MA0682", "", email
        ])


    colonne = [
        "#", "Matricola", "Cognome", "Nome", "Anno Freq.", "CFU",
        "Esito", "Svolgimento Esame", "Domande d'esame", "Data superamento",
        "Nota per lo studente", "CDS COD.", "AD COD.", "Misure Compensative", "Email"
    ]

    df_studenti = pd.DataFrame(dati_studenti, columns=colonne)

    # ---------------------------------------------------------
    # SCRITTURA SU EXCEL
    # ---------------------------------------------------------
    output_file = "Esempio_Appello_Ricostruito1.xlsx"

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df_header = pd.DataFrame(intestazioni)
        df_header.to_excel(writer, index=False, header=False, sheet_name="Foglio1")

        start_row = len(intestazioni)
        df_studenti.to_excel(writer, index=False, startrow=start_row, sheet_name="Foglio1")

    print(f"File generato: {output_file}")
n=10
for i in range (1,n):
    nome=f"appello_{i}.xlsx"
    genera_appello(nome)
