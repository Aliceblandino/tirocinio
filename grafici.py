# grafici.py
import pandas as pd

import plotly.express as px
## GRAFICI GLOBALI (credo a questo punto)
#boxplot
def grafico_boxplot_per_appello(df):
    fig = px.box(df, x="appello_id", y="voto", points="all", title="Boxplot per appello")
    print(df.columns)
    print(df.head())
    return fig.to_json()

#media globale
def grafico_media_globale(df):
    if df.empty:
        # Se non ci sono dati, ritorna grafico vuoto
        return {
            "data": [],
            "layout": {"title": "Media voti per appello"}
        }
    voti = pd.to_numeric(df["voto"], errors="coerce")#solo num
    df["voto_num"] = voti

    # Calcolo media per appello, ignorando valori NaN
    df_media = df.groupby("appello_id")["voto_num"].mean().reset_index()

    # Prepariamo i dati per Plotly
    graph = {
        "data": [{
            "x": df_media["appello_id"].tolist(),  # nomi degli appelli
            "y": df_media["voto_num"].tolist(),    # medie reali
            "type": "bar",
            "marker": {"color": "orange"},
            "text": [f"{v:.2f}" for v in df_media["voto_num"]],  # mostra valori sopra barre
            "textposition": "auto"
        }],
        "layout": {
            "title": "Media voti per appello",
            "xaxis": {"title": "Appello"},
            "yaxis": {"title": "Voto medio"},
            "margin": {"t": 50, "b": 100}  # spazio sotto per nomi appelli lunghi
        }
    }
    return graph
#DISTRIBUZIONE VOTI (SOLO SUFF)
def grafico_distribuzione_voti(df):
    if df.empty:
        return {
            "data": [],
            "layout": {"title": "Media voti per appello (SOLO SUFF)"}
        }

    df = df.copy()
    voti = pd.to_numeric(df["voto"], errors="coerce")

    df = df[voti >= 18]
    df["voto_num"] = voti[voti >= 18]

    df_media = df.groupby("appello_id")["voto_num"].mean().reset_index()

    graph = {
        "data": [{
            "x": df_media["appello_id"].tolist(),
            "y": df_media["voto_num"].tolist(),
            "type": "bar",
            "marker": {"color": "orange"},
            "text": [f"{v:.2f}" for v in df_media["voto_num"]],
            "textposition": "auto"
        }],
        "layout": {
            "title": "Media voti per appello (solo sufficienti)",
            "xaxis": {"title": "Appello"},
            "yaxis": {"title": "Voto medio"},
            "margin": {"t": 50, "b": 100}
        }
    }
    return graph
#PRIMO



def grafico_media_voti_solo(df):
    df_voti = df[df["tipo"] == "voto"]

    media = df_voti.groupby("appello_id")["voto"].mean().reset_index()

    fig = px.bar(media, x="appello_id", y="voto",
                 title="Media voti (solo studenti valutati)")
    return fig.to_json()

def grafico_esiti(df):
    conteggio = df["tipo"].value_counts().reset_index()
    conteggio.columns = ["tipo", "count"]

    fig = px.bar(conteggio, x="tipo", y="count",
                 title="Distribuzione esiti (voti, assenti, ritirati)")
    return fig.to_json()
#--Grafici singoli
def grafico_distribuzione_appello(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()

    voti = pd.to_numeric(df["voto"], errors="coerce")
    voti_validi = voti.dropna()

    conteggio = voti_validi.value_counts().sort_index()

    return {
        "data": [{
            "x": conteggio.index.tolist(),
            "y": conteggio.values.tolist(),
            "type": "bar",
            "marker": {"color": "orange"}
        }],
        "layout": {
            "title": f"Distribuzione voti",
            "xaxis": {"title": "Voto"},
            "yaxis": {"title": "Numero studenti"}
        }
    }
def grafico_boxplot_appello(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()

    voti = pd.to_numeric(df["voto"], errors="coerce")

    return {
        "data": [{
            "y": voti.tolist(),
            "type": "box",
            "name": f"Appello {appello_id}",
            "marker": {"color": "orange"}
        }],
        "layout": {
            "title": "Distribuzione statistica voti"
        }
    }
def grafico_esiti_appello(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()

    serie = df["voto"]
    voti_num = pd.to_numeric(serie, errors="coerce")

    assenti = (serie == "ASS").sum()
    ritirati = (serie == "RIT").sum()
    promossi = (voti_num >= 18).sum()
    bocciati = (voti_num < 18).sum()

    return {
        "data": [{
            "x": ["Promossi", "Bocciati", "Ritirati", "Assenti"],
            "y": [promossi, bocciati, ritirati, assenti],
            "type": "bar",
            "marker": {"color": "orange"}
        }],
        "layout": {
            "title": "Esiti appello"
        }
    }
def grafico_media_appello(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()

    voti = pd.to_numeric(df["voto"], errors="coerce")
    media = voti.mean()

    return {
        "data": [{
            "x": [f"Appello {appello_id}"],
            "y": [media],
            "type": "bar",
            "marker": {"color": "orange"},
            "text": [f"{media:.2f}"],
            "textposition": "auto"
        }],
        "layout": {
            "title": "Media voti",
            "yaxis": {"title": "Media"}
        }
    }