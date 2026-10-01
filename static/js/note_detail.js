
let archivoAEliminar = null;

// Función para obtener el token CSRF desde las cookies de Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function confirmarEliminarArchivo(id) {
    archivoAEliminar = id;
    document.getElementById('modal-confirmacion-archivo').classList.remove('hidden');
}

function eliminarArchivo(archivoId) {
    const csrfToken = getCookie('csrftoken');
    
    if (!csrfToken) {
        alert('Error: Token CSRF no encontrado. Recarga la página e intenta de nuevo.');
        return;
    }

    const btnConfirmar = document.getElementById('btn-confirmar-eliminar-archivo');
    const textoOriginal = btnConfirmar.innerHTML;
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = 'Eliminando...';

    // URL CORREGIDA (sin /notes/ al inicio si tu urls.py principal no tiene prefijo)
    fetch(`/attachment/eliminar/${archivoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'  // IMPORTANTE: envía las cookies de sesión
    })
    .then(response => {
        console.log('Status:', response.status);
        console.log('OK:', response.ok);
        
        // Intentar parsear como JSON, pero si falla, mostrar el texto
        return response.text().then(text => {
            try {
                return JSON.parse(text);
            } catch (e) {
                console.error('Respuesta no es JSON:', text);
                throw new Error('El servidor devolvió un error. Revisa la consola (F12).');
            }
        });
    })
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'No se pudo eliminar el archivo'));
        }
    })
    .catch(error => {
        console.error('Error completo:', error);
        alert('Error al eliminar: ' + error.message);
    })
    .finally(() => {
        btnConfirmar.disabled = false;
        btnConfirmar.innerHTML = textoOriginal;
        document.getElementById('modal-confirmacion-archivo').classList.add('hidden');
        archivoAEliminar = null;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Botones "Eliminar"
    document.querySelectorAll('.btn-eliminar-archivo').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const id = this.dataset.id;
            confirmarEliminarArchivo(id);
        });
    });

    // Botón "Cancelar"
    const btnCancelar = document.getElementById('btn-cancelar-eliminar-archivo');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function() {
            document.getElementById('modal-confirmacion-archivo').classList.add('hidden');
            archivoAEliminar = null;
        });
    }

    // Botón "Confirmar"
    const btnConfirmar = document.getElementById('btn-confirmar-eliminar-archivo');
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', function() {
            if (archivoAEliminar) {
                eliminarArchivo(archivoAEliminar);
            }
        });
    }

    // Cerrar modal al hacer clic fuera
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
