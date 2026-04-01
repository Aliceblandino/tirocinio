document.addEventListener("DOMContentLoaded", () => {

    // Dashboard
    const dashboard = document.querySelector('.container');
    if(dashboard){
        // Animazione cestino
        document.querySelectorAll('.delete-action').forEach(icon => {
            icon.addEventListener('click', (e) => {
                icon.classList.add('open');
                const card = icon.closest('.card');
                    card.style.transition = "0.4s";
                    card.style.opacity = "0";
                    card.style.transform = "scale(0.95)";
                    setTimeout(()=>card.remove(), 400);
                    icon.classList.remove('open');
            });
        });

        // Animazione pulsante "Visualizza grafico voti"
        document.querySelectorAll('.btn-grafico').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                dashboard.classList.add('zoom-out', 'page-transition');
                setTimeout(()=> window.location.href = btn.dataset.href, 500);
            });
        });
    }

    // Dettaglio appello
    const cardDettaglio = document.getElementById("card-dettaglio");
    if(cardDettaglio){
        // aggiunge la classe .show dopo un piccolo delay
        setTimeout(() => {
            cardDettaglio.classList.add("show");
        }, 50); // basta un ritardo minimo
    }
//GRAFICI DETTAGLIO APPELLO


    //cancella appello
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
