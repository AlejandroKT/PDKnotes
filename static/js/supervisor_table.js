document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filter-form');
    
    filterForm.addEventListener('submit', function(e) {
        const dateFromInput = document.getElementById('date_from');
        const dateToInput = document.getElementById('date_to');
        
        const dateFrom = dateFromInput.value;
        const dateTo = dateToInput.value;
        
        // Validar que ambas fechas estén presentes
        if (dateFrom && dateTo) {
            // Convertir a objetos Date para comparación precisa
            const fromDate = new Date(dateFrom);
            const toDate = new Date(dateTo);
            
            // Validar que fecha desde no sea mayor que fecha hasta
            if (fromDate > toDate) {
                e.preventDefault();
                alert('La fecha "Desde" no puede ser superior a la fecha "Hasta"');
                dateFromInput.focus();
                return false;
            }
        }
    });
    
    // Filas clickeables
    const clickableRows = document.querySelectorAll('.row-clickable');
    clickableRows.forEach(function(row) {
        row.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            
            const url = this.dataset.url;
            
            if (url) {
                window.location.href = url;
            }
        });
    });
});