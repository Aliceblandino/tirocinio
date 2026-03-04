import plotly.graph_objects as go
from collections import Counter


def grafico_distribuzione_voti(df):
    voti = []

    for v in df["Esito"].astype(str):
        v = v.strip()
        if v in ["", "nan", "ASS", "RIT", "0"]:
            voti.append("0")
        elif v in ["31", "30L"]:
            voti.append("30L")
        elif v.isdigit():
            voti.append(v)

    x_vals = ["0"] + [str(i) for i in range(18, 31)] + ["30L"]
    conteggio = Counter(voti)
    y_vals = [conteggio.get(v, 0) for v in x_vals]

    fig = go.Figure(
        data=[go.Bar(x=x_vals, y=y_vals)],
        layout=go.Layout(
            title="Distribuzione dei voti",
            xaxis_title="Voto (0 = insufficiente)",
            yaxis_title="Numero studenti",
            template="plotly_dark"
        )
    )

    return fig.to_json()
import plotly.express as px

def grafico_media_totale(df):
    media = df["voto"].mean()

    fig = px.bar(
        x=["Media complessiva"],
        y=[media],
        labels={"y": "Voto medio"},
        title="Media totale dei voti (tutti gli appelli)"
    )

    return fig.to_json()

def grafico_boxplot_per_appello(df):
    fig = px.box(
        df,
        x="materia",
        y="voto",
        title="Distribuzione voti per appello"
    )

    return fig.to_json()