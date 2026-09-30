# routes/dashboard.py
# Pagina principale con l'elenco degli appelli e i grafici riassuntivi.
from flask import Blueprint, render_template
from flask_login import login_required

from dati import lista_appelli, carica_tutti_i_voti, carica_ripetizioni
from grafici import *  # importa tutte le funzioni dai grafici

bp = Blueprint("dashboard", __name__)

#----------------- DASHBOARD ----------------
@bp.route("/dashboard")
@login_required
def dashboard():
    appelli = lista_appelli()
   # graph_media = None
    graph_box = None
    #graph_media_solo = None
    graph_media_globale = None
    graph_esiti = None
    graph_distribuzione_voti = None
    graph_genere = None
    graph_ripetizioni = None
    graph_ratio=None
    

    if appelli:
        df = carica_tutti_i_voti()
        if not df.empty:
            #graph_media = grafico_distribuzione_voti(df)
            graph_distribuzione_voti = grafico_distribuzione_voti(df)
            graph_box = grafico_boxplot_per_appello(df)
            #graph_media_solo = grafico_media_voti_solo(df)
            graph_media_globale = grafico_media_globale(df)
            graph_esiti = grafico_esiti(df)
            #graph_distribuzione_voti = grafico_distribuzione_voti(df)
            graph_genere = grafico_genere_per_appello(df)
            #graph_ripetizioni=grafico_ripetizioni(carica_ripetizioni())
            import json
            graph_ripetizioni = grafico_ripetizioni(carica_ripetizioni())
            parsed = json.loads(graph_ripetizioni)
            print("KEYS:", parsed.keys())
            print("DATA:", parsed.get("data"))
            graph_ratio = grafico_ratio_esiti(df)


    return render_template(
        "dashboard.html",
        appelli=appelli,
        graph_distribuzione_voti=graph_distribuzione_voti,
        #graph_media=graph_media,
        graph_box=graph_box,
        #graph_media_solo=graph_media_solo,
        graph_media_globale=graph_media_globale,
        graph_esiti=graph_esiti,
        graph_genere=graph_genere,
        graph_ripetizioni=graph_ripetizioni,
        graph_ratio=graph_ratio
    )
