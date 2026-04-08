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

function apriZoom(divId, plotData) {
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

    // Se NON è previsioni → nascondi slider
    if (divId !== "g-previsioni") {
        sliderWrapper.style.display = "none";
        return;
    }

    // Se è previsioni → mostra slider
    sliderWrapper.style.display = "block";

    // Range dinamico
    slider.min = 1;
    slider.max = plotData.max_anni;
    slider.value = plotData.default_anni;

    // Listener slider
    slider.oninput = () => {
        const n = parseInt(slider.value);

        let newLayout = JSON.parse(JSON.stringify(plotData.layout));
        let newData = JSON.parse(JSON.stringify(plotData.data));

        // Taglia le previsioni
        newData[1].x = newData[1].x.slice(0, n);
        newData[1].y = newData[1].y.slice(0, n);

        newLayout.title = `Previsione media voti (${n} appelli previsti)`;

        Plotly.newPlot("zoom-plot", newData, newLayout);
    };
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