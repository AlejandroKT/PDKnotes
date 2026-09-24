document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('supplier-search');
    const resultsDropdown = document.getElementById('search-results');
    const suppliersList = document.getElementById('suppliers-list');
    
    // Convertimos la lista de proveedores a un array de JavaScript
    const suppliers = Array.from(suppliersList.querySelectorAll('.supplier-item')).map(item => {
        const link = item.querySelector('a');
        return {
            name: item.dataset.name,
            document: item.dataset.document,
            url: link.href,
            displayName: item.querySelector('p.text-indigo-600').textContent,
            displayDocument: item.querySelector('p.text-gray-500').textContent
        };
    });
    
    // Evento al escribir en el input
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length === 0) {
            resultsDropdown.classList.add('hidden');
            return;
        }
        
        // Filtramos los proveedores que coincidan con el nombre o documento
        const filtered = suppliers.filter(supplier => 
            supplier.name.includes(query) || supplier.document.includes(query)
        );
        
        // Limpiamos el dropdown
        resultsDropdown.innerHTML = '';
        
        if (filtered.length === 0) {
            resultsDropdown.innerHTML = '<li class="px-4 py-2 text-sm text-gray-500">No se encontraron resultados</li>';
        } else {
            filtered.forEach(supplier => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <a href="${supplier.url}" class="block px-4 py-2 hover:bg-indigo-50 cursor-pointer">
                        <p class="text-sm font-medium text-gray-900">${supplier.displayName}</p>
                        <p class="text-xs text-gray-500">${supplier.displayDocument}</p>
                    </a>
                `;
                resultsDropdown.appendChild(li);
            });
        }
        
        resultsDropdown.classList.remove('hidden');
    });
    
    // Ocultar el dropdown al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !resultsDropdown.contains(e.target)) {
            resultsDropdown.classList.add('hidden');
        }
    });
});
