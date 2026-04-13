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
    # prendiamo solo i voti validi
    df_validi = df.dropna(subset=["voto"]).copy()
    df_validi["voto"] = df_validi["voto"].astype(float)

    # trasformiamo i voti in categorie
    def categ(v):
        if v < 18:
            return "Insufficiente"
        elif v == 31:
            return "30L"
        else:
            return str(int(v))

    df_validi["categoria"] = df_validi["voto"].apply(categ)

    # ordine categorie
    ordine = ["Insufficiente"] + [str(i) for i in range(18, 31)] + ["30L"]
    df_validi["categoria"] = pd.Categorical(df_validi["categoria"], categories=ordine, ordered=True)

    fig = go.Figure()
    for appello in df_validi["appello_id"].unique():
        df_app = df_validi[df_validi["appello_id"] == appello]

        fig.add_trace(go.Histogram(
            x=df_app["categoria"],
            name=f"Appello {appello}",
            opacity=0.6
        ))

    # Ordine asse X
    fig.update_xaxes(categoryorder="array", categoryarray=ordine)

    fig.update_layout(
        title="Distribuzione dei voti per appello",
        xaxis_title="Voto",
        yaxis_title="Frequenza",
        barmode="overlay"   # barre sovrapposte
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
#non funziona
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

#lienar regression voto medio futuro


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
    # prendiamo solo i voti validi
    df_validi = df.dropna(subset=["voto"]).copy()
    df_validi["voto"] = df_validi["voto"].astype(float)

    # trasformiamo i voti in categorie
    def categ(v):
        if v < 18:
            return "Insufficiente"
        elif v == 31:
            return "30L"
        else:
            return str(int(v))

    df_validi["categoria"] = df_validi["voto"].apply(categ)

    # ordine categorie
    ordine = ["Insufficiente"] + [str(i) for i in range(18, 31)] + ["30L"]
    df_validi["categoria"] = pd.Categorical(df_validi["categoria"], categories=ordine, ordered=True)

    fig = go.Figure()
    for appello in df_validi["appello_id"].unique():
        df_app = df_validi[df_validi["appello_id"] == appello]

        fig.add_trace(go.Histogram(
            x=df_app["categoria"],
            name=f"Appello {appello}",
            opacity=0.6
        ))

    # Ordine asse X
    fig.update_xaxes(categoryorder="array", categoryarray=ordine)

    fig.update_layout(
        title="Distribuzione dei voti per appello",
        xaxis_title="Voto",
        yaxis_title="Frequenza",
        barmode="overlay"   # barre sovrapposte
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
#media appello(3) TODO: da togliere
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
        line_color="orange"
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
        text=z_vals,
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
        .fillna(0)   # 🔥 fondamentale: niente NaN
    )

    fig = go.Figure()

    # Un tracciato radar per ogni appello
    for appello in df_pivot.index:
        valori = df_pivot.loc[appello].tolist()

        # 🔥 chiusura del poligono
        valori.append(valori[0])
        categorie_chiuse = categorie + [categorie[0]]

        fig.add_trace(go.Scatterpolar(
            r=valori,
            theta=categorie_chiuse,
            fill='toself',
            name=str(appello),
            opacity=0.6
        ))

    fig.update_layout(
        title="Radar ratio esiti per appello",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
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

    # 🔥 PREVISIONE ITERATIVA
    future_pred = []
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
#  MODELLO ENSEMBLE
# ============================

def mean_model(y):
    return np.mean(y)

def regression_model(x, y):
    b, a = np.polyfit(x, y, 1)
    next_x = len(x) + 1
    return a + b * next_x

def last_value_model(y):
    return y[-1]

def get_weights(n):
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

    w_m, w_r, w_l = get_weights(n)

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

#previsione tipologia esiti futuri
# def grafico_esiti_appello(df, appello_id):
#     df = df[df["appello_id"] == appello_id].copy()

#     serie = df["voto"]
#     voti_num = pd.to_numeric(serie, errors="coerce")

#     assenti = (serie == "ASS").sum()
#     ritirati = (serie == "RIT").sum()
#     promossi = (voti_num >= 18).sum()
#     bocciati = (voti_num < 18).sum()

#     return {
#         "data": [{
#             "x": ["Promossi", "Bocciati", "Ritirati", "Assenti"],
#             "y": [promossi, bocciati, ritirati, assenti],
#             "type": "bar",
#             "marker": {"color": "orange"}
#         }],
#         "layout": {
#             "title": "Esiti appello"
#         }
#     }

def estrai_storico_esiti(df):
    gruppi = df.groupby("appello_id")

    promossi = gruppi.apply(lambda g: (pd.to_numeric(g["voto"], errors="coerce") >= 18).sum()).tolist()
    bocciati = gruppi.apply(lambda g: (pd.to_numeric(g["voto"], errors="coerce") < 18).sum()).tolist()
    assenti  = gruppi.apply(lambda g: (g["voto"] == "ASS").sum()).tolist()
    ritirati = gruppi.apply(lambda g: (g["voto"] == "RIT").sum()).tolist()

    return promossi, bocciati, assenti, ritirati

def probabilita_storiche_esiti(df):
    conteggio = df["tipo"].value_counts()

    tot = conteggio.sum()

    p_prom = conteggio.get("promosso", 0) / tot
    p_bocc = conteggio.get("bocciato", 0) / tot
    p_ass  = conteggio.get("ASS", 0) / tot
    p_rit  = conteggio.get("RIT", 0) / tot

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
    import plotly.graph_objects as go

    # --- 1) Previsione iscritti (usa il tuo ensemble) ---
    df = df.copy()
    print(df.head(20))
    print(df.columns)
    df["data_appello"] = pd.to_datetime(df["data_appello"], dayfirst=True)

    df_count = (
        df.groupby(["appello_id", "data_appello"])
        .size()
        .reset_index(name="Iscritti")
        .sort_values("data_appello")
    )

    serie_storica = df_count["Iscritti"].tolist()
    n_storico = len(serie_storica)

    serie_prevista = forecast_iterativo(serie_storica.copy(), n_storico + n_future)
    iscritti_futuri = serie_prevista[-n_future:]

    ultima_data = df_count["data_appello"].iloc[-1]
    future_dates = [ultima_data + pd.Timedelta(days=30*(i+1)) for i in range(n_future)]

    # --- 2) Probabilità storiche globali (coerenti con grafico_esiti) ---
    p_prom, p_bocc, p_ass, p_rit = probabilita_storiche_esiti(df)
    print(f"Probabilità storiche - Promossi: {p_prom}, Bocciati: {p_bocc}, Assenti: {p_ass}, Ritirati: {p_rit}")
    # --- 3) Stima esiti futuri ---
    prom = []
    bocc = []
    ass  = []
    rit  = []

    for iscritti in iscritti_futuri:
        pred = stima_esiti_future_sessioni(iscritti, p_prom, p_bocc, p_ass, p_rit)
        prom.append(pred["promossi"])
        bocc.append(pred["bocciati"])
        ass.append(pred["assenti"])
        rit.append(pred["ritirati"])

    # --- 4) Grafico stacked bar ---
    fig = go.Figure()

    fig.add_trace(go.Bar(name="Promossi", x=future_dates, y=prom, marker=dict(color="green")))
    fig.add_trace(go.Bar(name="Bocciati", x=future_dates, y=bocc, marker=dict(color="red")))
    fig.add_trace(go.Bar(name="Assenti",  x=future_dates, y=ass,  marker=dict(color="gray")))
    fig.add_trace(go.Bar(name="Ritirati", x=future_dates, y=rit,  marker=dict(color="orange")))

    fig.update_layout(
        barmode="stack",
        title=f"Previsione esiti futuri (orizzonte: {n_future} appelli)",
        xaxis_title="Data appello",
        yaxis_title="Numero studenti",
        height=500
    )

    return fig.to_dict()