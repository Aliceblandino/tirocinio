// =========================
// FUNZIONI GLOBALI ZOOM
// =========================

const descrizioni = {
    "g-boxplot": "Il boxplot mostra la distribuzione dei voti, evidenziando mediana, quartili e outlier.",
    "g-media": "Questo grafico mostra l'andamento della media dei voti nei vari appelli.",
    "g-esiti": "Mostra la distribuzione degli esiti: promossi, bocciati, ritirati.",
    "g-dvoti": "Distribuzione completa dei voti ottenuti dagli studenti.",
    "g-genere": "Confronto tra voti e genere degli studenti.",
    "g-ripetizioni": "Mostra quanti studenti hanno ripetuto l'esame più volte.",
    "g-cumulativa": "Distribuzione cumulativa dei voti.",
    "g-previsioni": "Previsione dei voti futuri tramite regressione lineare."
};

// Grafici la cui struttura (tracce multiple: segmenti storici + previsti,
// subplot, bande di confidenza...) non permette di "tagliare" i dati lato
// client tramite un semplice slice degli array — per questi il valore dello
// slider va ricalcolato interamente dal server.
const PREVISIONI_RICALCOLO_SERVER = {
    "previsionemedie": "g-pmedie",
    "previsioneesiti": "g-previsioneesiti"
};

function apriZoom(divId, plotData, resultKey) {
    const modal = document.getElementById("zoom-modal");
    const zoomPlot = document.getElementById("zoom-plot");
    const zoomDesc = document.getElementById("zoom-description");

    const sliderWrapper = document.getElementById("zoom-slider-wrapper");
    const slider = document.getElementById("zoom-slider-previsioni");
    const sliderLabel = document.getElementById("zoom-slider-label");

    modal.style.display = "flex";

    // Disegna grafico iniziale
    Plotly.newPlot("zoom-plot", plotData.data, plotData.layout);

    // Descrizione
    zoomDesc.textContent = descrizioni[divId] || "Descrizione non disponibile.";

    // ============================
    // NUOVA LOGICA: controlla data-theme
    // ============================
    const originalDiv = document.getElementById(divId);
    const theme = originalDiv.getAttribute("data-theme");

    // Se NON è un grafico di previsioni → nascondi slider
    if (theme !== "previsioni") {
        sliderWrapper.style.display = "none";
        return;
    }

    // Se è previsioni → mostra slider
    sliderWrapper.style.display = "block";
    slider.oninput = null;

    if (resultKey in PREVISIONI_RICALCOLO_SERVER) {
        // Grafici a struttura complessa: lo slider richiede un ricalcolo
        // server-side (il client non sa quali tracce sono "storiche" e
        // quali "previste" senza rifare il lavoro del server).
        slider.min = 1;
        slider.max = 10;
        slider.value = 3;

        let debounceTimer = null;
        slider.oninput = () => {
            const n = parseInt(slider.value);
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => ricalcolaGraficoPrevisione(resultKey, n), 200);
        };
        return;
    }

    // Grafici semplici a 2 tracce (storico + previsione): taglio client-side
    slider.min = 1;
    slider.max = plotData.max_anni;
    slider.value = plotData.default_anni;

    // Listener slider
    slider.oninput = () => {
        const n = parseInt(slider.value);

        let newLayout = JSON.parse(JSON.stringify(plotData.layout));
        let newData = JSON.parse(JSON.stringify(plotData.data));

        // Taglia le previsioni (serie 1)
        newData[1].x = newData[1].x.slice(0, n);
        newData[1].y = newData[1].y.slice(0, n);

        newLayout.title = `Previsione media voti (${n} appelli previsti)`;

        Plotly.newPlot("zoom-plot", newData, newLayout);
    };
}

// Richiede al server il grafico di previsione ricalcolato con n_future = n
// e lo ridisegna nella modale di zoom. Usato per i grafici la cui struttura
// non è compatibile col semplice taglio client-side degli array.
function ricalcolaGraficoPrevisione(resultKey, n) {
    if (typeof getSelectedFilters !== "function") return;
    const filters = getSelectedFilters();

    fetch("/statistiche_globali_ajax", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            stats: ["previsioni"],
            appelli: filters.appelli,
            n_future: n
        })
    })
    .then(r => r.json())
    .then(data => {
        const raw = data[resultKey];
        const obj = typeof raw === "string" ? JSON.parse(raw) : raw;
        if (obj && obj.data && obj.layout) {
            Plotly.newPlot("zoom-plot", obj.data, obj.layout);
        }
    });
}


// =========================
// CODICE PRINCIPALE
// =========================

document.addEventListener("DOMContentLoaded", () => {

    // =========================
    // CHIUDI MODALE ZOOM
    // =========================
    const closeBtn = document.getElementById("zoom-close");
    if (closeBtn) {
        closeBtn.onclick = () => {
            document.getElementById("zoom-modal").style.display = "none";
        };
    }
    // Chiudi cliccando fuori dal contenuto
    const modal = document.getElementById("zoom-modal");
    if (modal) {
        modal.addEventListener("click", (e) => {
            // se clicchi sullo sfondo (non sul contenuto)
            if (e.target === modal) {
                modal.style.display = "none";
            }
        });
    }
    // Chiudi con ESC
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            const modal = document.getElementById("zoom-modal");
            if (modal) modal.style.display = "none";
        }
    });


    // =========================
    // DASHBOARD
    // =========================

    const dashboard = document.querySelector('.container');
    if (dashboard) {

        // Animazione cestino
        document.querySelectorAll('.delete-action').forEach(icon => {
            icon.addEventListener('click', () => {
                icon.classList.add('open');
                const card = icon.closest('.card');
                card.style.transition = "0.4s";
                card.style.opacity = "0";
                card.style.transform = "scale(0.95)";
                setTimeout(() => card.remove(), 400);
                icon.classList.remove('open');
            });
        });

        // Animazione pulsante "Visualizza grafico voti"
        document.querySelectorAll('.btn-grafico').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                dashboard.classList.add('zoom-out', 'page-transition');
                setTimeout(() => window.location.href = btn.dataset.href, 500);
            });
        });
    }

    // =========================
    // DETTAGLIO APPELLO
    // =========================

    const cardDettaglio = document.getElementById("card-dettaglio");
    if (cardDettaglio) {
        setTimeout(() => {
            cardDettaglio.classList.add("show");
        }, 50);
    }

    // =========================
    // CANCELLA APPELLO
    // =========================

    document.querySelectorAll(".delete-action").forEach(icon => {
        icon.addEventListener("click", () => {
            const id = icon.getAttribute("data-id");
            const form = document.getElementById(`form-delete-${id}`);

            if (form) {
                if (confirm("Sei sicuro di voler eliminare questo appello?")) {
                    form.submit();
                }
            } else {
                console.error("Form di eliminazione non trovata per id", id);
            }
        });
    });

});