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
#esiti appello (1)
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