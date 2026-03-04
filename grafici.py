# grafici.py
import plotly.graph_objs as go
import json
from plotly.utils import PlotlyJSONEncoder
import pandas as pd

# ------------------ Grafico singolo appello ------------------
def grafico_distribuzione_voti(df):
    """
    Genera un istogramma della distribuzione dei voti di un singolo appello
    df: DataFrame con colonna 'Esito'
    Ritorna JSON pronto per Plotly
    """
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df['Esito'],
        nbinsx=30,
        marker_color='lightgreen'
    ))
    fig.update_layout(
        title="Distribuzione voti",
        xaxis_title="Voti",
        yaxis_title="Conteggio",
        template='plotly_white',
        height=400
    )
    return fig.to_json()

# ------------------ Media totale per appello ------------------
def grafico_media_totale(df):
    """
    Grafico a barre: media voti per appello con nome materia
    """
    medie = df.groupby('appello_id')['voto'].mean().reset_index()
    
    # Prendiamo la prima materia per ogni appello_id
    materie = df.groupby('appello_id')['materia'].first().reset_index()
    
    # Uniamo le due tabelle
    medie = medie.merge(materie, on='appello_id')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=medie['materia'],
        y=medie['voto'],
        text=medie['voto'].round(2),
        textposition='auto',
        marker_color='lightblue'
    ))
    fig.update_layout(
        title="Media voti per appello",
        xaxis_title="Appello",
        yaxis_title="Media voti",
        template='plotly_white',
        height=400
    )
    return fig.to_json()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=medie['materia'],
        y=medie['voto'],
        text=medie['voto'].round(2),
        textposition='auto',
        marker_color='lightblue'
    ))
    fig.update_layout(
        title="Media voti per appello",
        xaxis_title="Appello",
        yaxis_title="Media voti",
        template='plotly_white',
        height=400
    )
    return fig.to_json()

# ------------------ Boxplot per appello ------------------
def grafico_boxplot_per_appello(df):
    """
    Genera un boxplot con un box per ogni appello
    df: DataFrame con colonne ['voto', 'appello_id', 'materia']
    """
    fig = go.Figure()
    for appello_id, gruppo in df.groupby("appello_id"):
        fig.add_trace(go.Box(
            y=gruppo['voto'],
            name=gruppo['materia'].iloc[0],
            boxmean='sd',  # mostra media e deviazione standard
            marker_color='lightblue'
        ))
    fig.update_layout(
        title="Distribuzione voti per appello",
        yaxis=dict(title="Voti"),
        xaxis=dict(title="Appello"),
        boxmode='group',
        template='plotly_white',
        height=400
    )
    return fig.to_json()