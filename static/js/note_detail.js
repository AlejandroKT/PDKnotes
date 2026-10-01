let archivoAEliminar = null;

function confirmarEliminarArchivo(id) {
    archivoAEliminar = id;
    document.getElementById('modal-confirmacion-archivo').classList.remove('hidden');
}

function eliminarArchivo(archivoId) {
    // Obtenemos el token CSRF del meta tag (ver paso 5)
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    if (!csrfToken) {
        console.error('CSRF token no encontrado.');
        alert('Error de seguridad: Token CSRF no encontrado en la página.');
        return;
    }

    // Deshabilitar botón temporalmente para evitar doble clic
    const btnConfirmar = document.getElementById('btn-confirmar-eliminar-archivo');
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = '<svg class="animate-spin h-4 w-4 mr-1" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Eliminando...';

    fetch(`/notes/attachment/eliminar/${archivoId}/`, { // Asegúrate que '/notes/' coincide con el prefijo de tu app
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Recarga la página para actualizar la vista
        } else {
            alert('Error al eliminar: ' + (data.error || 'Desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión al intentar eliminar el archivo.');
    })
    .finally(() => {
        // Restaurar el botón
        btnConfirmar.disabled = false;
        btnConfirmar.innerHTML = `<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg> Sí, Eliminar`;
        document.getElementById('modal-confirmacion-archivo').classList.add('hidden');
        archivoAEliminar = null;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // 1. Botones "Eliminar"
    document.querySelectorAll('.btn-eliminar-archivo').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Evita conflictos con otros clicks
            const id = this.dataset.id;
            confirmarEliminarArchivo(id);
        });
    });

    // 2. Botón "Cancelar" del modal
    const btnCancelar = document.getElementById('btn-cancelar-eliminar-archivo');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function() {
            document.getElementById('modal-confirmacion-archivo').classList.add('hidden');
            archivoAEliminar = null;
        });
    }

    // 3. Botón "Confirmar Eliminar" del modal
    const btnConfirmar = document.getElementById('btn-confirmar-eliminar-archivo');
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', function() {
            if (archivoAEliminar) {
                eliminarArchivo(archivoAEliminar);
            }
        });
    }

    // 4. Cerrar modal al hacer clic fuera de él (en el fondo oscuro)
    const modal = document.getElementById('modal-confirmacion-archivo');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                document.getElementById('modal-confirmacion-archivo').classList.add('hidden');
                archivoAEliminar = null;
            }
        });
    }
});
