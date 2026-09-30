# routes/statistiche.py
# Statistiche globali (pagina e aggiornamento AJAX dei grafici).
import pandas as pd
from flask import Blueprint, render_template, request
from flask_login import login_required

from dati import lista_appelli, carica_tutti_i_voti, carica_ripetizioni
from grafici import *  # importa tutte le funzioni dai grafici

bp = Blueprint("statistiche", __name__)

# ---------------- STATISTICHE GLOBALI ----------------
@bp.route("/statistiche_globali_ajax", methods=["POST"])
@login_required
def statistiche_globali_ajax():
    print("\n===== AJAX DEBUG =====")
    print("POST JSON:", request.json)

    selected_stats = request.json.get("stats", [])
    selected_appelli = request.json.get("appelli", [])

    print("Selected stats:", selected_stats)
    print("Selected appelli:", selected_appelli)

    selected_appelli = [str(a) for a in selected_appelli]

    df = carica_tutti_i_voti(selected_appelli)

    print("DF filtrato appelli:", df["appello_id"].unique())
    print("DF rows:", len(df))
    print("DF columns:",len(df))
    print("DF columns:", df.columns.tolist())
    print(df.head())
    # =========================
    # CALCOLO MEDIE STORICHE
    # =========================
    df_media = (
        df[df["tipo"] == "promosso"]
        .groupby("appello_id")["voto"]
        .apply(lambda x: pd.to_numeric(x, errors="coerce").mean())
        .reset_index(name="media")
    )

    medie_storiche = df_media["media"].tolist()
    # ===== PREPARA PROMOSSI E ISCRITTI =====
    promossi, bocciati, assenti, ritirati = estrai_storico_esiti(df)

    iscritti = [
        p + b + a + r
        for p, b, a, r in zip(promossi, bocciati, assenti, ritirati)
    ]

    # ===== PREVISIONE MEDIE =====
    # n_future = int(request.json.get("n_future", 5))

    # medie_predette = forecast_exam_means(
    #     promossi,
    #     iscritti,
    #     medie_storiche,
    #     len(medie_storiche) + n_future
    # )


    print("\n=== DEBUG MEDIE STORICHE ===")
    print(df_media)
    print("Lista medie:", medie_storiche)
    results = {}

    if "voti" in selected_stats:
        print("Genero grafico: voti")
        print("Genero grafico: boxplot")
        print("Genero grafico: media")
        print("Genero grafico: esiti + cumulativa")
        results["voti"] = grafico_distribuzione_voti(df)
        results["boxplot"] = grafico_boxplot_per_appello(df)
        results["media"] = grafico_media_globale(df)
        results["esiti"] = grafico_esiti(df)
        results["cumulativa"] = grafico_distribuzione_cumulativa(df)
        results["ratio"] = grafico_ratio_esiti(df)
        results["heatmap"] = heatmap_voti(df) #???
        results["tasso"] = grafico_tasso_superamento(df)
        results["kpi"] = kpi_riepilogo(df)
    else:
        print("NON genero voti")
        print("NON genero boxplot")
        print("NON genero media")
        print("NON genero esiti")

    if "affluenza" in selected_stats:
        print("Genero grafico: genere")
        results["genere"] = grafico_genere_per_appello(df)
        print("Genero grafico: ripetizioni")
        df_rip = carica_ripetizioni(selected_appelli)
        results["ripetizioni"] = grafico_ripetizioni(df_rip)
    else:
        print("NON genero genere")
        print("NON genero ripetizioni")

    if "previsioni" in selected_stats:
        print("Genero grafico: previsioni")
        results["previsioni"] = grafico_previsione(df)
        # Previsione iscritti (grafico nuovo)
        n_future = int(request.json.get("n_future", 5))
        results["previsioneiscritti"] = grafico_previsioni_iscritti(df, n_future)
        results["previsioneesiti"] = grafico_previsione_esiti_futuri(df, n_future)
        results["previsionemedie"] = grafico_previsione_medie(df, n_future)

    else:
        print("NON genero previsioni")

    #n_future = int(request.json.get("n_future", 5))
    #results["previsioni"] = grafico_previsioni_iscritti(df, n_future)

   
        
    
    # n_future = int(request.json.get("n_future", 5))
    # results["previsioni"] = grafico_previsioni_iscritti(df, n_future)

    print("RISULTATI AJAX:", results.keys())
    print("=====================\n")

    return results

@bp.route("/statistiche_globali", methods=["GET", "POST"])
@login_required
def statistiche_globali():
    appelli = lista_appelli()

    # --- DEFAULT ---
    selected_stats = [ "voti", "affluenza", "previsioni"]
    selected_appelli = [str(a["id"]) for a in appelli]  # TUTTO STRINGA

    # --- SE ARRIVA UN POST, LEGGO I FILTRI ---
    if request.method == "POST":
        selected_stats = request.form.getlist("stats")
        selected_appelli = request.form.getlist("appelli")
        selected_appelli = [str(a) for a in selected_appelli]  # normalizzo

    # --- PREPARO I GRAFICI ---
    graph_box = None
    graph_media_globale = None
    graph_esiti = None
    graph_distribuzione_voti = None
    graph_cumulativa = None
    graph_genere = None
    graph_ripetizioni = None
    graph_previsione=None
    graph_heatmap=None
    graph_ratio=None
    graph_piscritti=None
    graph_previsioneesiti=None
    graph_pmedie=None
    graph_tasso=None
    kpi=None


    # --- SE CI SONO APPELLI CARICATI ---
    if appelli:

        # CARICO I VOTI DEGLI APPELLI SELEZIONATI
        df = carica_tutti_i_voti(selected_appelli)

        # SE IL DF NON È VUOTO, GENERO SOLO I GRAFICI SELEZIONATI
        if not df.empty:

            if "voti" in selected_stats:
                graph_distribuzione_voti = grafico_distribuzione_voti(df)
                graph_box = grafico_boxplot_per_appello(df)
                graph_esiti = grafico_esiti(df)
                graph_cumulativa = grafico_distribuzione_cumulativa(df)
                graph_heatmap = heatmap_voti(df) #non so se esite
                graph_media_globale = grafico_media_globale(df)
                graph_tasso = grafico_tasso_superamento(df)
                kpi = kpi_riepilogo(df)

            if "affluenza" in selected_stats:
                graph_ratio= grafico_ratio_esiti(df)
                graph_genere = grafico_genere_per_appello(df)
                df_rip = carica_ripetizioni(selected_appelli)
                graph_ripetizioni = grafico_ripetizioni(df_rip)

            if "previsioni" in selected_stats:
                graph_previsione = grafico_previsione(df)
                graph_piscritti = grafico_previsioni_iscritti(df, n_future=5)
                graph_previsioneesiti = grafico_previsione_esiti_futuri(df, n_future=5)
                graph_pmedie = grafico_previsione_medie(df, n_future=5)
        
            


    # --- RENDER TEMPLATE ---
    return render_template(
        "statistiche.html",
        appelli=appelli,
        selected_stats=selected_stats,
        selected_appelli=selected_appelli,
        graph_distribuzione_voti=graph_distribuzione_voti,
        graph_box=graph_box,
        graph_media_globale=graph_media_globale,
        graph_esiti=graph_esiti,
        graph_cumulativa=graph_cumulativa,
        graph_genere=graph_genere,
        graph_ripetizioni=graph_ripetizioni,
        graph_previsione=graph_previsione,
        graph_heatmap=graph_heatmap,
        graph_ratio=graph_ratio,
        graph_piscritti=graph_piscritti,
        graph_previsioneesiti=graph_previsioneesiti,
        graph_pmedie=graph_pmedie,
        graph_tasso=graph_tasso,
        kpi=kpi
    )
