document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todas las filas clickeables
    const clickableRows = document.querySelectorAll('.row-clickable');
    
    // Agregar event listener a cada fila
    clickableRows.forEach(function(row) {
        row.addEventListener('click', function(e) {
            // Prevenir que se active si se hace clic en un enlace dentro de la fila
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            
            // Obtener la URL del data attribute
            const url = this.dataset.url;
            
            // Navegar a la URL
            if (url) {
                window.location.href = url;
            }
        });
    });
});
