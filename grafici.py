# grafici.py
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression


## GRAFICI GLOBALI (credo a questo punto)
#boxplot (1)
def grafico_boxplot_per_appello(df):
    fig = px.box(df, x="appello_id", y="voto", points="all", title="Boxplot per appello")
    print(df.columns)
    print(df.head())
    return fig.to_json()

#media globale (2)
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
#Distribuzione esiti (3)
def grafico_esiti(df):
    conteggio = df["tipo"].value_counts().reset_index()
    conteggio.columns = ["tipo", "count"]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=conteggio["tipo"].tolist(),
        y=conteggio["count"].tolist()
    ))

    fig.update_layout(
        title="Distribuzione esiti",
        xaxis_title="Esito",
        yaxis_title="Numero studenti"
    )

    return fig.to_json()

#distribuzione voti solo sufficienti (4)
def grafico_distribuzione_voti(df):
    if df.empty:
        # Se non ci sono dati, ritorna grafico vuoto
        return {
            "data": [],
            "layout": {"title": "Media voti per appello (solo sufficienti)"}
        }
    voti = pd.to_numeric(df["voto"], errors="coerce")#solo num
    df["voto_num"] = voti
    df = df[df["voto_num"] >= 18]

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
            "title": "Media voti per appello(solo sufficienti)",
            "xaxis": {"title": "Appello"},
            "yaxis": {"title": "Voto medio"},
            "margin": {"t": 50, "b": 100}  # spazio sotto per nomi appelli lunghi
        }
    }
    return graph
#distribuzione cumulativa bruttino (5)
def grafico_distribuzione_cumulativa(df):
    df_validi = df.dropna(subset=["voto"]).copy()
    df_validi["voto"] = df_validi["voto"].astype(float)

    # Trasformiamo i voti in categorie
    def categ(v):
        if v < 18:
            return "Insufficiente"
        elif v == 31:
            return "30L"
        else:
            return str(int(v))

    df_validi["categoria"] = df_validi["voto"].apply(categ)

    # Ordine categorie
    ordine = ["Insufficiente"] + [str(i) for i in range(18, 31)] + ["30L"]

    # Pivot: righe = categoria, colonne = appello_id, valori = conteggi
    tabella = (
        df_validi
        .groupby(["categoria", "appello_id"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=ordine, fill_value=0)
    )

    fig = go.Figure()

    # Una barra per ogni appello (stacked)
    for appello in tabella.columns:
        fig.add_trace(go.Bar(
            x=tabella.index,
            y=tabella[appello],
            name=f"Appello {appello}"
        ))

    fig.update_layout(
        barmode="stack",
        title="Distribuzione dei voti per appello",
        xaxis_title="Voto",
        yaxis_title="Numero studenti",
        height=600
    )

    return fig.to_json()

#distribuzione maschi/femmine per appello (6)
def grafico_genere_per_appello(df):
    fig = px.histogram(
        df,
        x="appello_id",
        color="Genere",
        barmode="group",
        title="Distribuzione maschi/femmine per appello",
        category_orders={"Genere": ["M", "F", "?"]},
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_layout(
        xaxis_title="Appello",
        yaxis_title="Numero studenti"
    )

    return fig.to_json()

def grafico_ripetizioni(df):
    conteggio_ripetizioni = df["matricola"].value_counts()
    df_tentativi = conteggio_ripetizioni.value_counts().sort_index()

    x = list(map(int, df_tentativi.index.tolist()))
    y = list(map(int, df_tentativi.values.tolist()))

    fig = go.Figure(
        data=[
            go.Bar(
                x=x,
                y=y,
                marker=dict(color="#636efa")
            )
        ]
    )

    fig.update_layout(
        title="Quante volte gli studenti hanno sostenuto l'esame",
        xaxis_title="Numero di tentativi",
        yaxis_title="Numero di studenti",
        xaxis=dict(tickmode='linear', dtick=1)
    )

    return fig.to_json()

#GRAFICI NUOVI

#tasso di superamento nel tempo (promossi / iscritti, per appello, ordinato per data)
def grafico_tasso_superamento(df):
    df = df.copy()
    df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()
    df["data_appello"] = pd.to_datetime(df["data_appello"], dayfirst=True, errors="coerce")

    if df.empty:
        return {"data": [], "layout": {"title": "Tasso di superamento per appello"}}

    gruppi = df.groupby(["appello_id", "data_appello"])

    tabella = gruppi.apply(
        lambda g: pd.Series({
            "promossi": (g["tipo"] == "promosso").sum(),
            "iscritti": len(g)
        })
    ).reset_index().sort_values("data_appello")

    tabella["tasso"] = (tabella["promossi"] / tabella["iscritti"] * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tabella["data_appello"].dt.strftime("%d/%m/%Y").tolist(),
        y=tabella["tasso"].tolist(),
        mode="lines+markers+text",
        text=[f"{v}%" for v in tabella["tasso"]],
        textposition="top center",
        line=dict(color="#2ca02c", width=3),
        marker=dict(size=8),
        name="Tasso di superamento",
        customdata=tabella["appello_id"].tolist(),
        hovertemplate="Appello: %{customdata}<br>Data: %{x}<br>Superamento: %{y}%<extra></extra>"
    ))

    fig.update_layout(
        title="Tasso di superamento per appello (promossi / iscritti)",
        xaxis_title="Data appello",
        yaxis_title="% Promossi",
        yaxis=dict(range=[0, 100]),
        height=450
    )

    return fig.to_dict()

#pannello KPI riassuntivo (non un grafico plotly: numeri di sintesi)
def kpi_riepilogo(df):
    if df.empty:
        return {
            "totale_iscritti": 0,
            "tasso_superamento": None,
            "voto_medio": None,
            "deviazione_std": None,
            "tasso_assenza": None
        }

    df = df.copy()
    df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()
    voti_num = pd.to_numeric(df["voto"], errors="coerce")
    voti_promossi = voti_num[df["tipo"] == "promosso"]

    totale = len(df)
    promossi = (df["tipo"] == "promosso").sum()
    assenti = (df["tipo"] == "assente").sum()

    return {
        "totale_iscritti": int(totale),
        "tasso_superamento": round(float(promossi) / totale * 100, 1) if totale else None,
        "voto_medio": round(float(voti_promossi.mean()), 2) if not voti_promossi.empty else None,
        "deviazione_std": round(float(voti_promossi.std()), 2) if len(voti_promossi) > 1 else None,
        "tasso_assenza": round(float(assenti) / totale * 100, 1) if totale else None
    }


#--Grafici singoli
# Distribuzione voti(1)
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
#boxplot (2)
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
#esiti appello (5)
def grafico_esiti_appello(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()

    # Usiamo direttamente la colonna "tipo"
    conteggi = df["tipo"].value_counts()

    labels = ["promosso", "bocciato", "assente", "ritirato"]
    values = [int(conteggi.get(l, 0)) for l in labels]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Promossi", "Bocciati", "Assenti", "Ritirati"],
        y=values,
        marker_color="orange"
    ))

    fig.update_layout(
        title=f"Esiti appello {appello_id}",
        xaxis_title="Esito",
        yaxis_title="Numero studenti"
    )

    return fig.to_json()
#kpi appello: tasso di superamento + confronto con media storica del corso (sostituisce il vecchio grafico_media_appello, ridondante col box media)
def kpi_appello(df, appello_id):
    df = df.copy()
    df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()

    df_app = df[df["appello_id"] == appello_id]
    df_altri = df[df["appello_id"] != appello_id]

    voti_app = pd.to_numeric(df_app["voto"], errors="coerce")
    voti_promossi_app = voti_app[df_app["tipo"] == "promosso"]

    voti_altri = pd.to_numeric(df_altri["voto"], errors="coerce")
    voti_promossi_altri = voti_altri[df_altri["tipo"] == "promosso"]

    totale = len(df_app)
    promossi = int((df_app["tipo"] == "promosso").sum())

    media_voto = round(float(voti_promossi_app.mean()), 2) if not voti_promossi_app.empty else None
    media_storica = round(float(voti_promossi_altri.mean()), 2) if not voti_promossi_altri.empty else None
    delta = round(media_voto - media_storica, 2) if media_voto is not None and media_storica is not None else None

    return {
        "media_voto": media_voto,
        "tasso_superamento": round(float(promossi) / totale * 100, 1) if totale else None,
        "media_storica_corso": media_storica,
        "delta_vs_storico": delta
    }
#grafico maschi/femmine per appello (4)
def grafico_genere_uno(df, appello_id):
    df = df[df["appello_id"] == appello_id]
    fig = px.histogram(
        df,
        x="Genere",
        color="Genere",
        category_orders={"Genere": ["M", "F", "?"]},
        color_discrete_sequence=px.colors.qualitative.Set2,
        title=f"Distribuzione maschi/femmine – Appello {appello_id}"
    )
    fig.update_layout(
        xaxis_title="Genere",
        yaxis_title="Numero studenti",
        showlegend=False
    )
    return fig.to_json()

#donut esiti (7)
def grafico_esiti_donut(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()

    conteggi = df["tipo"].value_counts()
    labels = ["promosso", "bocciato", "assente", "ritirato"]
    values = [int(conteggi.get(l, 0)) for l in labels]
    colori = {"promosso": "#2ca02c", "bocciato": "#d62728", "assente": "#7f7f7f", "ritirato": "#ff7f0e"}

    fig = go.Figure(data=[go.Pie(
        labels=["Promossi", "Bocciati", "Assenti", "Ritirati"],
        values=values,
        hole=0.5,
        marker=dict(colors=[colori[l] for l in labels]),
        textinfo="label+percent"
    )])

    fig.update_layout(title=f"Esiti appello {appello_id}")
    return fig.to_dict()

#ecdf / cumulata voti (8)
def grafico_ecdf_voti(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    voti = pd.to_numeric(df["voto"], errors="coerce").dropna().sort_values()

    if voti.empty:
        return {"data": [], "layout": {"title": "Distribuzione cumulativa voti"}}

    n = len(voti)
    percentuali = [round((i + 1) / n * 100, 1) for i in range(n)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=voti.tolist(),
        y=percentuali,
        mode="lines+markers",
        line=dict(shape="hv", color="#1f77b4"),
        name="% cumulativa"
    ))

    fig.update_layout(
        title=f"Distribuzione cumulativa voti - Appello {appello_id}",
        xaxis_title="Voto",
        yaxis_title="% studenti con voto ≤ x",
        yaxis=dict(range=[0, 100])
    )
    return fig.to_dict()

#voti ordinati / ranking (9)
def grafico_voti_ordinati(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    voti = pd.to_numeric(df["voto"], errors="coerce").dropna().sort_values().reset_index(drop=True)

    if voti.empty:
        return {"data": [], "layout": {"title": "Voti ordinati"}}

    colori = ["#d62728" if v < 18 else "#2ca02c" for v in voti]

    fig = go.Figure(data=[go.Bar(
        x=list(range(1, len(voti) + 1)),
        y=voti.tolist(),
        marker=dict(color=colori)
    )])

    fig.update_layout(
        title=f"Voti ordinati - Appello {appello_id}",
        xaxis_title="Posizione in classifica",
        yaxis_title="Voto"
    )
    return fig.to_dict()

#esiti per genere (10)
def grafico_esiti_per_genere(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()

    categorie = ["promosso", "bocciato", "assente", "ritirato"]
    etichette = {"promosso": "Promossi", "bocciato": "Bocciati", "assente": "Assenti", "ritirato": "Ritirati"}

    fig = go.Figure()
    for genere in ["M", "F", "?"]:
        sotto = df[df["Genere"] == genere]
        if sotto.empty:
            continue
        conteggi = sotto["tipo"].value_counts()
        fig.add_trace(go.Bar(
            name=genere,
            x=[etichette[c] for c in categorie],
            y=[int(conteggi.get(c, 0)) for c in categorie]
        ))

    fig.update_layout(
        barmode="group",
        title=f"Esiti per genere - Appello {appello_id}",
        xaxis_title="Esito",
        yaxis_title="Numero studenti"
    )
    return fig.to_dict()

#gauge tasso di superamento (11)
def grafico_gauge_superamento(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()

    totale = len(df)
    promossi = int((df["tipo"] == "promosso").sum())
    tasso = round(promossi / totale * 100, 1) if totale else 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=tasso,
        number={"suffix": "%"},
        title={"text": f"Tasso di superamento - Appello {appello_id}"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#2ca02c"},
            "steps": [
                {"range": [0, 40], "color": "#f8d7da"},
                {"range": [40, 70], "color": "#fff3cd"},
                {"range": [70, 100], "color": "#d4edda"}
            ]
        }
    ))
    return fig.to_dict()

#media voto per genere (12)
def grafico_media_per_genere(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    df["voto_num"] = pd.to_numeric(df["voto"], errors="coerce")

    df_media = df.groupby("Genere")["voto_num"].mean().round(2).dropna()

    fig = go.Figure(data=[go.Bar(
        x=df_media.index.tolist(),
        y=df_media.values.tolist(),
        text=[f"{v:.2f}" for v in df_media.values],
        textposition="auto",
        marker=dict(color="#9467bd")
    )])

    fig.update_layout(
        title=f"Voto medio per genere - Appello {appello_id}",
        xaxis_title="Genere",
        yaxis_title="Voto medio"
    )
    return fig.to_dict()

#distribuzione voti per anno di frequenza (13)
def grafico_voti_per_anno_freq(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    if "anno_freq" not in df.columns:
        return {"data": [], "layout": {"title": "Dato Anno Freq. non disponibile"}}

    df["voto_num"] = pd.to_numeric(df["voto"], errors="coerce")
    df = df.dropna(subset=["anno_freq"])

    fig = go.Figure()
    for anno in sorted(df["anno_freq"].dropna().unique()):
        sotto = df[df["anno_freq"] == anno]["voto_num"].dropna()
        if sotto.empty:
            continue
        fig.add_trace(go.Box(y=sotto.tolist(), name=str(anno)))

    fig.update_layout(
        title=f"Distribuzione voti per anno di frequenza - Appello {appello_id}",
        xaxis_title="Anno di frequenza",
        yaxis_title="Voto"
    )
    return fig.to_dict()

#tasso di superamento per anno di frequenza (14)
def grafico_tasso_per_anno_freq(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    if "anno_freq" not in df.columns:
        return {"data": [], "layout": {"title": "Dato Anno Freq. non disponibile"}}

    df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()
    df = df.dropna(subset=["anno_freq"])

    righe = []
    for anno in sorted(df["anno_freq"].dropna().unique()):
        sotto = df[df["anno_freq"] == anno]
        totale = len(sotto)
        promossi = (sotto["tipo"] == "promosso").sum()
        righe.append((str(anno), round(promossi / totale * 100, 1) if totale else 0))

    if not righe:
        return {"data": [], "layout": {"title": "Dato Anno Freq. non disponibile"}}

    anni, tassi = zip(*righe)

    fig = go.Figure(data=[go.Bar(
        x=list(anni),
        y=list(tassi),
        text=[f"{t}%" for t in tassi],
        textposition="auto",
        marker=dict(color="#17becf")
    )])

    fig.update_layout(
        title=f"Tasso di superamento per anno di frequenza - Appello {appello_id}",
        xaxis_title="Anno di frequenza",
        yaxis_title="% Promossi",
        yaxis=dict(range=[0, 100])
    )
    return fig.to_dict()

#presenza vs distanza (15)
def grafico_presenza_distanza(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    if "svolgimento" not in df.columns:
        return {"data": [], "layout": {"title": "Dato Svolgimento Esame non disponibile"}}

    mappa = {"P": "Presenza", "D": "Distanza"}
    conteggi = df["svolgimento"].map(mappa).value_counts()

    if conteggi.empty:
        return {"data": [], "layout": {"title": "Dato Svolgimento Esame non disponibile"}}

    fig = go.Figure(data=[go.Bar(
        x=conteggi.index.tolist(),
        y=conteggi.values.tolist(),
        marker=dict(color="#8c564b")
    )])

    fig.update_layout(
        title=f"Presenza vs Distanza - Appello {appello_id}",
        xaxis_title="Modalità",
        yaxis_title="Numero studenti"
    )
    return fig.to_dict()

#distribuzione a fasce di voto (16)
def grafico_fasce_voto(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()
    voti = pd.to_numeric(df["voto"], errors="coerce").dropna()

    if voti.empty:
        return {"data": [], "layout": {"title": "Distribuzione a fasce di voto"}}

    def fascia(v):
        if v < 18:
            return "Insufficiente"
        elif v <= 22:
            return "18-22"
        elif v <= 26:
            return "23-26"
        elif v <= 29:
            return "27-29"
        else:
            return "30-30L"

    ordine = ["Insufficiente", "18-22", "23-26", "27-29", "30-30L"]
    conteggi = voti.apply(fascia).value_counts().reindex(ordine, fill_value=0)

    fig = go.Figure(data=[go.Bar(
        x=conteggi.index.tolist(),
        y=conteggi.values.tolist(),
        marker=dict(color=["#d62728", "#ff7f0e", "#ffbb33", "#8bc34a", "#2ca02c"])
    )])

    fig.update_layout(
        title=f"Distribuzione a fasce di voto - Appello {appello_id}",
        xaxis_title="Fascia",
        yaxis_title="Numero studenti"
    )
    return fig.to_dict()


#statistiche miste(0)
def statistiche_appello(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()

    # Converti voto in numerico (30L → 31)
    voti = pd.to_numeric(df["voto"].replace("30L", 31), errors="coerce")

    # Tieni solo i voti validi
    voti_validi = voti.dropna()

    if voti_validi.empty:
        return {
            "media": None,
            "mediana": None,
            "moda": None,
            "deviazione_std": None,
            "minimo": None,
            "massimo": None,
            "varianza": None,
            "difficoltà": None
        }

    media = voti_validi.mean()
    mediana = voti_validi.median()

    # Moda può avere più valori → prendiamo il primo
    try:
        moda = voti_validi.mode().iloc[0]
    except:
        moda = None

    deviazione_std = voti_validi.std()
    minimo = voti_validi.min()
    massimo = voti_validi.max()
    vatrianza = voti_validi.var()
    difficoltà = (1 - (voti_validi >= 18).mean())*100  # % di bocciati

    return {
        "media": round(media, 2),
        "mediana": round(mediana, 2),
        "moda": int(moda) if moda is not None else None,
        "deviazione_std": round(deviazione_std, 2),
        "minimo": int(minimo),
        "massimo": int(massimo),
        "varianza": round(vatrianza, 2),
        "difficoltà": round(difficoltà, 2)
    }
#radarchart (6)
def grafico_statistiche_radar(df, appello_id):
    df = df[df["appello_id"] == appello_id].copy()

    voti = pd.to_numeric(df["voto"].replace("30L", 31), errors="coerce")
    voti_validi = voti.dropna()

    if voti_validi.empty:
        return go.Figure().to_json()

    mediana = voti_validi.median()
    moda = voti_validi.mode().iloc[0]
    dev_std = voti_validi.std()
    #varianza = voti_validi.var()
    media= voti_validi.mean()
    minimo = voti_validi.min()
    massimo = voti_validi.max()

    categorie = ["Mediana", "Moda", "Dev.Std", "Media", "Minimo", "Massimo"]
    valori = [mediana, moda, dev_std, media, minimo, massimo]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valori,
        theta=categorie,
        fill='toself',
        name=f"Appello {appello_id}",
        line_color="orange",
        text=[f"{v:.2f}" for v in valori],
        mode="lines+markers+text",
        textposition="top center"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 31])
        ),
        showlegend=False,
        title=f"Statistiche Appello {appello_id}"
    )

    return fig.to_json()


#grafici comuni
#non è comune e non funziona davvero


def heatmap_voti(df):


    df = df.copy()

    # Normalizza voti
    df["voto"] = df["voto"].astype(str).str.strip().str.upper()
    df["voto"] = df["voto"].replace({"30L": "31"})

    # Converti in numerico
    df["Voto_num"] = pd.to_numeric(df["voto"], errors="coerce")

    # Tieni solo voti validi
    df_validi = df[df["Voto_num"].notna()]


    if df_validi.empty:
        fig = go.Figure()
        fig.update_layout(title="Nessun voto numerico disponibile")
        return fig.to_dict()

    # Pivot: righe = appelli, colonne = voti
    df_pivot = (
        df_validi.groupby(["appello_id", "Voto_num"])
        .size()
        .reset_index(name="Conteggio")
        .pivot(index="appello_id", columns="Voto_num", values="Conteggio")
        .fillna(0)
    )

    df_pivot.columns = df_pivot.columns.astype(str)

    z_vals = df_pivot.values.tolist()
    x_vals = df_pivot.columns.tolist()
    y_vals = df_pivot.index.tolist()

    fig = go.Figure(
        data=go.Heatmap(
            z=z_vals,
            x=x_vals,
            y=y_vals,
            colorscale="YlGnBu",
            colorbar=dict(title="N° studenti"),
            hovertemplate="Appello: %{y}<br>Voto: %{x}<br>Conteggio: %{z}<extra></extra>",
        )
    )


    fig.update_traces(
        xgap=0, ygap=0,
        text=[[int(v) if v else "" for v in row] for row in z_vals],
        texttemplate="%{text}",
        textfont=dict(size=10, color="black")
    )

    fig.update_layout(
        title="Distribuzione voti per appello",
        xaxis_title="Voto",
        yaxis_title="Appello"
    )

    return fig.to_dict()


def grafico_ratio_esiti(df):
    df = df.copy()

    # Normalizza tipo esito (FIX: usare .str.lower())
    df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()

    # Mappatura coerente
    df["Esito"] = df["tipo"].replace({
        "promosso": "Promossi",
        "bocciato": "Bocciati",
        "assente": "Assenti",
        "ritirato": "Ritirati"
    })

    categorie = ["Promossi", "Bocciati", "Assenti", "Ritirati"]

    # Conteggio per appello e categoria
    df_count = (
        df.groupby(["appello_id", "Esito"])
        .size()
        .reset_index(name="Conteggio")
    )

    # Totale per appello
    totali = df.groupby("appello_id").size().rename("Totale")
    df_count = df_count.merge(totali, on="appello_id")

    # Ratio (0–1)
    df_count["Ratio"] = (df_count["Conteggio"] / df_count["Totale"]).round(3)

    # Pivot
    df_pivot = (
        df_count.pivot(index="appello_id", columns="Esito", values="Ratio")
        .reindex(columns=categorie)
        .fillna(0)   # niente NaN
    )

    fig = go.Figure()

    # Un tracciato radar per ogni appello
    for appello in df_pivot.index:
        valori = df_pivot.loc[appello].tolist()

        # chiusura del poligono
        valori_chiusi = valori + [valori[0]]
        categorie_chiuse = categorie + [categorie[0]]
        etichette = [f"{v*100:.0f}%" for v in valori_chiusi]

        fig.add_trace(go.Scatterpolar(
            r=valori_chiusi,
            theta=categorie_chiuse,
            fill='toself',
            name=str(appello),
            opacity=0.6,
            text=etichette,
            mode="lines+markers+text",
            textposition="top center"
        ))

    fig.update_layout(
        title="Radar ratio esiti per appello",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickformat=".0%"
            )
        ),
        showlegend=True,
        height=500
    )

    return fig.to_dict()


#PREVISIONI GLOBALI
#da finire
def previsione_iscritti(df):
    # df deve contenere: appello_id, totale_iscritti
    df = df.copy()

    if "totale_iscritti" not in df.columns:
        return None

    # Ordina gli appelli in ordine temporale
    df = df.sort_values("appello_id")

    iscritti = df["totale_iscritti"].values

    # Serve almeno 2 appelli
    if len(iscritti) < 2:
        return None

    # X = 0,1,2,... per la regressione
    X = np.arange(len(iscritti)).reshape(-1, 1)
    y = iscritti

    model = LinearRegression()
    model.fit(X, y)

    # Previsione per il prossimo appello
    next_x = np.array([[len(iscritti)]])
    prev = model.predict(next_x)[0]

    return max(0, int(prev))  # niente numeri negativi


#lienar regression voto medio futuro
def grafico_previsione(df):
    # Controlli base
    if df.empty or "voto" not in df.columns or "data_appello" not in df.columns:
        return {
            "data": [],
            "layout": {"title": "Previsione media voti"},
            "max_anni": 1,
            "default_anni": 1
        }

    # Conversioni
    df["voto_num"] = pd.to_numeric(df["voto"], errors="coerce")
    df["data_appello"] = pd.to_datetime(df["data_appello"], errors="coerce")
    df_validi = df.dropna(subset=["voto_num", "data_appello"])

    # Media per appello
    df_media = df_validi.groupby(["appello_id", "data_appello"])["voto_num"].mean().reset_index()
    df_media = df_media.sort_values("data_appello")

    n_appelli = len(df_media)
    if n_appelli < 2:
        return {
            "data": [],
            "layout": {"title": "Dati insufficienti per una previsione"},
            "max_anni": 1,
            "default_anni": 1
        }

    # Asse X = giorni dal primo appello
    df_media["giorni"] = (df_media["data_appello"] - df_media["data_appello"].min()).dt.days
    X = df_media["giorni"].values.reshape(-1, 1)
    y = df_media["voto_num"].values

    # Distanza media tra appelli (minimo 30 giorni)
    distanze = df_media["data_appello"].diff().dt.days.dropna()
    media_distanza = max(30, int(distanze.mean()))

    # Numero previsioni future = numero appelli storici
    n_future = n_appelli

    # errore storico del modello, usato per costruire la banda di confidenza
    model_base = LinearRegression().fit(X, y)
    residui = y - model_base.predict(X)
    errore_std = float(np.std(residui)) if len(residui) > 1 else 0.0

    # PREVISIONE ITERATIVA
    future_pred = []
    future_upper = []
    future_lower = []
    future_dates = []

    current_X = X.copy()
    current_y = y.copy()
    last_date = df_media["data_appello"].max()

    for i in range(n_future):
        # Regressione aggiornata
        model = LinearRegression()
        model.fit(current_X, current_y)

        # Prossima data
        next_date = last_date + pd.Timedelta(days=media_distanza)
        last_date = next_date
        future_dates.append(next_date)

        # Converti in giorni
        next_day = (next_date - df_media["data_appello"].min()).days

        # Predizione
        next_pred = model.predict([[next_day]])[0]

        # Limiti realistici
        next_pred = float(np.clip(next_pred, 18, 31))

        # la banda si allarga man mano che ci si allontana nel futuro
        margine = errore_std * (1 + i * 0.3)
        future_upper.append(float(np.clip(next_pred + margine, 0, 31)))
        future_lower.append(float(np.clip(next_pred - margine, 0, 31)))

        # Salva
        future_pred.append(next_pred)

        # Aggiorna dataset per la prossima iterazione
        current_X = np.append(current_X, [[next_day]], axis=0)
        current_y = np.append(current_y, next_pred)

    # Dati grafico
    storico_x = df_media["data_appello"].dt.strftime("%d/%m/%Y").tolist()
    storico_y = df_media["voto_num"].tolist()

    previsioni_x = [d.strftime("%d/%m/%Y") for d in future_dates]
    previsioni_y = future_pred

    data = [
        {
            "x": storico_x,
            "y": storico_y,
            "type": "scatter",
            "mode": "lines+markers",
            "marker": {"color": "orange"},
            "name": "Storico"
        },
        {
            "x": previsioni_x,
            "y": previsioni_y,
            "type": "scatter",
            "mode": "lines+markers",
            "marker": {"color": "red"},
            "name": "Previsioni"
        },
        {
            "x": previsioni_x + previsioni_x[::-1],
            "y": future_upper + future_lower[::-1],
            "type": "scatter",
            "fill": "toself",
            "fillcolor": "rgba(255,0,0,0.12)",
            "line": {"width": 0},
            "hoverinfo": "skip",
            "name": "Intervallo previsione",
            "showlegend": True
        }
    ]

    layout = {
        "title": "Previsione media voti",
        "xaxis": {"title": "Data appello"},
        "yaxis": {"title": "Media voto", "range": [0, 31]},
        "margin": {"t": 50, "b": 100}
    }

    return {
        "data": data,
        "layout": layout,
        "max_anni": n_future,
        "default_anni": min(3, n_future)
    }


##PREVISONI
import numpy as np
import plotly.graph_objects as go

# ============================
#  MODELLO ENSEMBLE (ISCRITTI)
# ============================

def mean_model(y):
    return np.mean(y)

def regression_model(x, y):
    b, a = np.polyfit(x, y, 1)
    next_x = len(x) + 1
    return a + b * next_x

def last_value_model(y):
    return y[-1]

def get_weights_iscritti(n):
    if n <= 3:
        return 0.5, 0.2, 0.3   # media, regressione, ultimo valore
    elif n <= 10:
        return 0.3, 0.5, 0.2
    else:
        return 0.2, 0.7, 0.1

def ensemble_predict(y):
    n = len(y)
    x = np.arange(1, n + 1)

    m = mean_model(y)
    r = regression_model(x, y)
    l = last_value_model(y)

    w_m, w_r, w_l = get_weights_iscritti(n)

    prediction = (w_m * m) + (w_r * r) + (w_l * l)
    return prediction

def forecast_iterativo(data, n_finale):
    serie = data.copy()

    while len(serie) < n_finale:
        next_val = ensemble_predict(serie)
        serie.append(next_val)

    return serie

# ============================
#  GRAFICO
# ============================

def grafico_previsioni_iscritti(df, n_future=5):
    print("\n=== PREVISIONI ISCRITTI (ENSEMBLE) ===")

    df = df.copy()

    # Assicuriamoci che la data sia datetime
    df["data_appello"] = pd.to_datetime(df["data_appello"], dayfirst=True)

    # Conta iscritti per appello
    df_count = (
        df.groupby(["appello_id", "data_appello"])
        .size()
        .reset_index(name="Iscritti")
        .sort_values("data_appello")
    )

    # Serie storica
    serie_storica = df_count["Iscritti"].tolist()
    n_storico = len(serie_storica)

    # Numero totale punti finali
    n_finale = n_storico + n_future

    # Previsione iterativa
    serie_prevista = forecast_iterativo(serie_storica.copy(), n_finale)

    # Costruzione asse X
    date_storiche = df_count["data_appello"].tolist()
    ultima_data = date_storiche[-1]

    future_dates = [ultima_data + pd.Timedelta(days=30 * (i+1)) for i in range(n_future)]

    # Grafico
    fig = go.Figure()

    # Storico
    fig.add_trace(go.Scatter(
        x=date_storiche,
        y=serie_storica,
        mode="lines+markers",
        name="Storico iscritti"
    ))

    # Previsioni
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=serie_prevista[-n_future:],
        mode="lines+markers",
        name="Previsione iscritti",
        line=dict(dash="dash")
    ))

    fig.update_layout(
        title=f"Previsione iscritti (orizzonte: {n_future} appelli)",
        xaxis_title="Data appello",
        yaxis_title="Numero iscritti",
        height=500
    )

    return fig.to_dict()

def estrai_storico_esiti(df):
    gruppi = df.groupby("appello_id")

    promossi = gruppi.apply(lambda g: (pd.to_numeric(g["voto"], errors="coerce") >= 18).sum()).tolist()
    bocciati = gruppi.apply(lambda g: (pd.to_numeric(g["voto"], errors="coerce") < 18).sum()).tolist()
    assenti  = gruppi.apply(lambda g: (g["tipo"] == "assente").sum()).tolist()
    ritirati = gruppi.apply(lambda g: (g["tipo"] == "ritirato").sum()).tolist()

    print("\n=== DEBUG: Storico esiti ===")
    print("Promossi:", promossi)
    print("Bocciati:", bocciati)
    print("Assenti:", assenti)
    print("Ritirati:", ritirati)

    return promossi, bocciati, assenti, ritirati

def probabilita_storiche_esiti(df):
    conteggio = df["tipo"].value_counts()

    print("\n=== DEBUG: Conteggio esiti globali ===")
    print(conteggio)

    tot = conteggio.sum()

    p_prom = conteggio.get("promosso", 0) / tot
    p_bocc = conteggio.get("bocciato", 0) / tot
    p_ass  = conteggio.get("assente", 0) / tot
    p_rit  = conteggio.get("ritirato", 0) / tot

    print(f"Probabilità storiche - Promossi: {p_prom}, Bocciati: {p_bocc}, Assenti: {p_ass}, Ritirati: {p_rit}")

    return p_prom, p_bocc, p_ass, p_rit

def stima_esiti_future_sessioni(iscritti_previsti, p_prom, p_bocc, p_ass, p_rit):
    return {
        "promossi": round(iscritti_previsti * p_prom),
        "bocciati": round(iscritti_previsti * p_bocc),
        "assenti":  round(iscritti_previsti * p_ass),
        "ritirati": round(iscritti_previsti * p_rit)
    }

def predict_outcomes(
    iscritti_previsti,
    promossi,
    bocciati,
    assenti,
    ritirati,
    pesi=None,          # es: [0.2, 0.3, 0.5]
    normalize=True,     # normalizza probabilità
    round_values=True   # arrotonda output
):
    """
    Predice promossi, bocciati, assenti e ritirati dato N iscritti.

    Parameters:
    - iscritti_previsti: int
    - promossi, bocciati, assenti, ritirati: liste storiche
    - pesi: lista pesi (opzionale, stessa lunghezza dei dati)
    - normalize: forza somma probabilità = 1
    - round_values: arrotonda risultati finali

    Returns:
    - dict con risultati
    """

    # --- STEP 1: conversione in array ---
    promossi = np.array(promossi)
    bocciati = np.array(bocciati)
    assenti  = np.array(assenti)
    ritirati = np.array(ritirati)

    iscritti = promossi + bocciati + assenti + ritirati

    # --- STEP 2: calcolo proporzioni ---
    p_prom = promossi / iscritti
    p_bocc = bocciati / iscritti
    p_ass  = assenti  / iscritti
    p_rit  = ritirati / iscritti

    # --- STEP 3: pesi ---
    if pesi is None:
        pesi = np.ones(len(iscritti)) / len(iscritti)
    else:
        pesi = np.array(pesi)
        pesi = pesi / np.sum(pesi)  # normalizza

    # --- STEP 4: media pesata ---
    p_prom_mean = np.sum(pesi * p_prom)
    p_bocc_mean = np.sum(pesi * p_bocc)
    p_ass_mean  = np.sum(pesi * p_ass)
    p_rit_mean  = np.sum(pesi * p_rit)

    # --- STEP 5: normalizzazione (sicurezza) ---
    if normalize:
        total = p_prom_mean + p_bocc_mean + p_ass_mean + p_rit_mean
        p_prom_mean /= total
        p_bocc_mean /= total
        p_ass_mean  /= total
        p_rit_mean  /= total

    # --- STEP 6: applica a N ---
    prom_pred = iscritti_previsti * p_prom_mean
    bocc_pred = iscritti_previsti * p_bocc_mean
    ass_pred  = iscritti_previsti * p_ass_mean
    rit_pred  = iscritti_previsti * p_rit_mean

    # --- STEP 7: arrotondamento ---
    if round_values:
        prom_pred = round(prom_pred)
        bocc_pred = round(bocc_pred)
        ass_pred  = round(ass_pred)
        rit_pred  = round(rit_pred)

    return {
        "iscritti": iscritti_previsti,
        "promossi": prom_pred,
        "bocciati": bocc_pred,
        "assenti": ass_pred,
        "ritirati": rit_pred,
        "probabilità": {
            "promossi": p_prom_mean,
            "bocciati": p_bocc_mean,
            "assenti": p_ass_mean,
            "ritirati": p_rit_mean
        }
    }

def grafico_previsione_esiti_futuri(df, n_future=5):
    from plotly.subplots import make_subplots

    print("\n=== PREVISIONE ESITI FUTURI (CONFRONTO STORICO + FUTURO) ===")
    print(df.head(20))
    print("Colonne:", df.columns)
    print("Tipi unici:", df["tipo"].unique())

    df = df.copy()
    df["data_appello"] = pd.to_datetime(df["data_appello"], dayfirst=True)

    # ============================================================
    # 1) ESITI STORICI PER OGNI APPELLO
    # ============================================================
    gruppi = df.groupby("data_appello")

    storico_prom = gruppi.apply(lambda g: (pd.to_numeric(g["voto"], errors="coerce") >= 18).sum()).tolist()
    storico_bocc = gruppi.apply(lambda g: (pd.to_numeric(g["voto"], errors="coerce") < 18).sum()).tolist()
    storico_ass  = gruppi.apply(lambda g: (g["tipo"] == "assente").sum()).tolist()
    storico_rit  = gruppi.apply(lambda g: (g["tipo"] == "ritirato").sum()).tolist()

    date_storiche = sorted(df["data_appello"].unique())

    print("\n=== DEBUG: Esiti storici ===")
    print("Date storiche:", date_storiche)
    print("Promossi storici:", storico_prom)
    print("Bocciati storici:", storico_bocc)
    print("Assenti storici:", storico_ass)
    print("Ritirati storici:", storico_rit)

    # ============================================================
    # 2) PREVISIONE ISCRITTI FUTURI (ENSEMBLE)
    # ============================================================
    df_count = (
        df.groupby(["appello_id", "data_appello"])
        .size()
        .reset_index(name="Iscritti")
        .sort_values("data_appello")
    )

    serie_storica = df_count["Iscritti"].tolist()
    serie_prevista = forecast_iterativo(serie_storica.copy(), len(serie_storica) + n_future)
    iscritti_futuri = serie_prevista[-n_future:]

    print("\nIscritti futuri previsti:", iscritti_futuri)

    ultima_data = df_count["data_appello"].iloc[-1]
    future_dates = [ultima_data + pd.Timedelta(days=30*(i+1)) for i in range(n_future)]

    print("Date future:", future_dates)

    # ============================================================
    # 3) PROBABILITÀ STORICHE GLOBALI
    # ============================================================
    p_prom, p_bocc, p_ass, p_rit = probabilita_storiche_esiti(df)

    # ============================================================
    # 4) STIMA ESITI FUTURI
    # ============================================================
    fut_prom = []
    fut_bocc = []
    fut_ass  = []
    fut_rit  = []

    for iscritti in iscritti_futuri:
        pred = stima_esiti_future_sessioni(iscritti, p_prom, p_bocc, p_ass, p_rit)
        fut_prom.append(pred["promossi"])
        fut_bocc.append(pred["bocciati"])
        fut_ass.append(pred["assenti"])
        fut_rit.append(pred["ritirati"])

    print("\n=== DEBUG: Previsioni esiti futuri ===")
    print("Promossi futuri:", fut_prom)
    print("Bocciati futuri:", fut_bocc)
    print("Assenti futuri:", fut_ass)
    print("Ritirati futuri:", fut_rit)

    # ============================================================
    # 5) GRAFICO SMALL-MULTIPLE: STORICO E FUTURO AFFIANCATI
    # ============================================================
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Storico", "Previsto"),
        shared_yaxes=True
    )

    colori = {"Promossi": "green", "Bocciati": "red", "Assenti": "gray", "Ritirati": "orange"}

    fig.add_trace(go.Bar(name="Promossi", x=date_storiche, y=storico_prom, marker=dict(color=colori["Promossi"]), legendgroup="Promossi"), row=1, col=1)
    fig.add_trace(go.Bar(name="Bocciati", x=date_storiche, y=storico_bocc, marker=dict(color=colori["Bocciati"]), legendgroup="Bocciati"), row=1, col=1)
    fig.add_trace(go.Bar(name="Assenti",  x=date_storiche, y=storico_ass,  marker=dict(color=colori["Assenti"]),  legendgroup="Assenti"),  row=1, col=1)
    fig.add_trace(go.Bar(name="Ritirati", x=date_storiche, y=storico_rit,  marker=dict(color=colori["Ritirati"]), legendgroup="Ritirati"), row=1, col=1)

    fig.add_trace(go.Bar(name="Promossi", x=future_dates, y=fut_prom, marker=dict(color=colori["Promossi"]), legendgroup="Promossi", showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(name="Bocciati", x=future_dates, y=fut_bocc, marker=dict(color=colori["Bocciati"]), legendgroup="Bocciati", showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(name="Assenti",  x=future_dates, y=fut_ass,  marker=dict(color=colori["Assenti"]),  legendgroup="Assenti",  showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(name="Ritirati", x=future_dates, y=fut_rit,  marker=dict(color=colori["Ritirati"]), legendgroup="Ritirati", showlegend=False), row=1, col=2)

    fig.update_layout(
        barmode="stack",
        title="Confronto esiti: storico vs futuro previsto",
        yaxis_title="Numero studenti",
        height=600
    )
    return fig.to_dict()


#Previsione delle medie

#1.componenti
def mean_model_medie(medie):
    return np.mean(medie)

def last_value_model_medie(medie):
    return medie[-1]

def regression_model_medie(promossi, iscritti, medie):
    # pass_rate
    p = np.array(promossi) / np.array(iscritti)
    y = np.array(medie)

    # regressione: y = a + b*p
    X = np.vstack([np.ones(len(p)), p]).T
    coeffs = np.linalg.lstsq(X, y, rcond=None)[0]

    return coeffs  # a, b


def predict_regression(coeffs, prom_prev, iscritti_prev):
    p = prom_prev / iscritti_prev
    a, b = coeffs
    return a + b * p

#2.pesi adattivi
def get_weights_medie(n):
    if n <= 5:
        return 0.5, 0.2, 0.3   # media, regressione, last
    elif n <= 20:
        return 0.3, 0.5, 0.2
    else:
        return 0.2, 0.7, 0.1

def predict_exam_mean(prom, isc, med, prom_prev, iscritti_prev):
    import numpy as np

    # --- 1) Media mobile degli ultimi 3 valori ---
    if len(med) >= 3:
        ma3 = np.mean(med[-3:])
    else:
        ma3 = np.mean(med)

    # --- 2) Trend lineare su tutta la serie ---
    X = np.arange(len(med))
    Y = np.array(med)
    if len(med) >= 2:
        coeffs = np.polyfit(X, Y, 1)
        trend_pred = coeffs[0] * len(med) + coeffs[1]
    else:
        trend_pred = med[-1]

    # --- 3) Dinamica: differenza (delta) ---
    if len(med) >= 2:
        delta = med[-1] - med[-2]
    else:
        delta = 0

    # --- 4) Accelerazione: differenza delle differenze ---
    if len(med) >= 3:
        accel = (med[-1] - med[-2]) - (med[-2] - med[-3])
    else:
        accel = 0

    # --- 5) Pass-rate ---
    ratio = prom_prev / iscritti_prev if iscritti_prev > 0 else 1
    ratio_adj = 18 + (ratio * 12)  # 18–30

    # --- 6) Ensemble pattern-based ---
    pred = (
        0.30 * ma3 +        # stabilità
        0.25 * trend_pred + # direzione generale
        0.20 * (med[-1] + delta) +  # segue la dinamica
        0.15 * (med[-1] + delta + accel) +  # segue accelerazione
        0.10 * ratio_adj    # realismo basato sul pass-rate
    )

    # --- 7) Limiti realistici ---
    pred = max(18, min(pred, 30))

    return {"media_predetta": pred}

def forecast_exam_means(promossi, iscritti, medie, n_finale):
    """
    Genera una serie predetta delle medie fino a n_finale.
    """
    prom = promossi.copy()
    isc = iscritti.copy()
    med = medie.copy()
    print("\n=== PREVISIONE ITERATIVA MEDIE D'ESAME ===")
    print("Promossi storici:", prom)
    print("Iscritti storici:", isc)
    print("Medie storiche:", med)

    while len(med) < n_finale:
        pred = predict_exam_mean(
            prom,
            isc,
            med,
            prom_prev=prom[-1],
            iscritti_prev=isc[-1]
        )["media_predetta"]

        # aggiungo la previsione
        med.append(pred)

        # opzionale: puoi anche prevedere promossi/iscritti
        # per ora li manteniamo costanti
        prom.append(prom[-1])
        isc.append(isc[-1])
    print("Medie previste:", med)

    return med

def grafico_previsione_medie(df, n_future):
    df["voto_num"] = pd.to_numeric(df["voto"], errors="coerce")
    df_media = df.groupby("appello_id")["voto_num"].mean().reset_index()

    medie_storiche = df_media["voto_num"].tolist()
    etichette_storiche = df_media["appello_id"].tolist()

    promossi = df[df["tipo"] == "promosso"].groupby("appello_id").size().tolist()
    iscritti = df.groupby("appello_id").size().tolist()

    # Previsioni future
    n_finale = len(medie_storiche) + n_future
    medie_predette = forecast_exam_means(promossi, iscritti, medie_storiche, n_finale)

    n_storico = len(medie_storiche)
    n_pred = len(medie_predette) - n_storico

    # X storiche e future
    x_storico = list(range(1, n_storico + 1))
    x_pred = list(range(n_storico + 1, n_storico + 1 + n_pred))

    # Etichette asse X
    etichette_future = [f"appello futuro {i+1}" for i in range(n_pred)]
    etichette_x = etichette_storiche + etichette_future
    tickvals = x_storico + x_pred

    fig = go.Figure()

    #storico
    for i in range(len(medie_storiche) - 1):
        y0 = medie_storiche[i]
        y1 = medie_storiche[i+1]
        colore_linea = "green" if y1 > y0 else "red"

        fig.add_trace(go.Scatter(
            x=[x_storico[i], x_storico[i+1]],
            y=[y0, y1],
            mode="lines",
            line=dict(color=colore_linea, width=3),
            showlegend=False,
            hoverinfo="skip"
        ))

    #pallini storici (colori dinamici)
    fig.add_trace(go.Scatter(
        x=x_storico,
        y=medie_storiche,
        mode="markers",
        marker=dict(
            size=10,
            color=["red" if v < 18 else "green" for v in medie_storiche]
        ),
        name="Medie storiche",
        hovertemplate="Storico<br>Appello: %{x}<br>Media: %{y:.2f}<extra></extra>"
    ))

    #previsione (colori dinamici)
    future_vals = medie_predette[n_storico:]

    for i in range(len(future_vals) - 1):
        y0 = future_vals[i]
        y1 = future_vals[i+1]
        colore_linea = "green" if y1 > y0 else "red"

        fig.add_trace(go.Scatter(
            x=[x_pred[i], x_pred[i+1]],
            y=[y0, y1],
            mode="lines",
            line=dict(color=colore_linea, width=3, dash="dash"),
            showlegend=False,
            hoverinfo="skip"
        ))

    #pallini predetti
    fig.add_trace(go.Scatter(
        x=x_pred,
        y=future_vals,
        mode="markers",
        marker=dict(
            size=10,
            color=["red" if v < 18 else "orange" for v in future_vals]
        ),
        name="Medie predette",
        hovertemplate="Previsione<br>Appello: %{x}<br>Media: %{y:.2f}<extra></extra>"
    ))

    #collegamento tra ultimo storico e primo predetto
    if n_pred > 0:
        fig.add_trace(go.Scatter(
            x=[x_storico[-1], x_pred[0]],
            y=[medie_storiche[-1], future_vals[0]],
            mode="lines",
            line=dict(color="gray", width=2, dash="dot"),
            showlegend=False
        ))

    #area di confidenza ±5%
    tutte = medie_predette
    upper = [v * 1.05 for v in tutte]
    lower = [v * 0.95 for v in tutte]

    fig.add_trace(go.Scatter(
        x=tickvals,
        y=upper,
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=tickvals,
        y=lower,
        mode="lines",
        fill="tonexty",
        fillcolor="rgba(200,200,200,0.2)",
        line=dict(width=0),
        name="Intervallo ±5%",
        hoverinfo="skip"
    ))


    #linea "Inizio previsione"
    fig.add_vline(
        x=n_storico + 0.5,
        line_width=2,
        line_dash="dot",
        line_color="gray"
    )

    fig.add_annotation(
        x=n_storico + 0.5,
        y=max(medie_predette),
        text="Inizio previsione",
        showarrow=False,
        yshift=10,
        font=dict(color="gray", size=10)
    )

    #asse x con etichette storiche + future
    fig.update_xaxes(
        tickmode="array",
        tickvals=tickvals,
        ticktext=etichette_x
    )

    fig.update_layout(
        title="Andamento delle Medie d'Esame (storico + previsione)",
        xaxis_title="Appello",
        yaxis_title="Media",
        template="plotly_white",
        legend=dict(x=0.01, y=0.99)
    )

    return fig.to_plotly_json()
