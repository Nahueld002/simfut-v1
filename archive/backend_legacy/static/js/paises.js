document.addEventListener("DOMContentLoaded", function () {
    listarPaises();

    document.getElementById("formPais").addEventListener("submit", function (e) {
        e.preventDefault();
        guardarPais();
    });
});

function listarPaises() {
    fetch('/api/paises/listar')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("#tablaPaises tbody");
            tbody.innerHTML = "";

            data.data.forEach((item, index) => {
                const rowClass = index % 2 === 0 ? 'bg-gray-800/30' : 'bg-transparent';
                
                const tr = document.createElement("tr");
                tr.className = `hover:bg-gray-700/50 transition-colors ${rowClass}`;
                tr.innerHTML = `
                    <td class="p-4 font-medium text-white">${item.nombre}</td>
                    <td class="p-4 font-mono text-green-400">${item.codigofifa}</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded bg-gray-700 text-gray-300 text-xs font-semibold">
                            ${item.nombreconfederacion}
                        </span>
                    </td>
                    <td class="p-4 text-center">
                        <div class="flex items-center justify-center gap-2">
                            <button onclick="editarPais(${item.paisid})" class="p-1.5 bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white rounded transition-all" title="Editar">
                                <i data-lucide="edit-2" class="w-4 h-4"></i>
                            </button>
                            <button onclick="eliminarPais(${item.paisid})" class="p-1.5 bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white rounded transition-all" title="Eliminar">
                                <i data-lucide="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            lucide.createIcons();
        })
        .catch(error => console.error("Error cargando países:", error));
}

function abrirModalNuevo() {
    document.getElementById("tituloModal").innerText = "Crear País";
    document.getElementById("txtPaisID").value = "0";
    document.getElementById("txtNombre").value = "";
    document.getElementById("txtCodigoFIFA").value = "";
    cargarConfederaciones();
    mostrarModal();
}

function cargarConfederaciones(seleccionado = null) {
    fetch('/api/paises/confederaciones')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById("selectConfederacion");
            select.innerHTML = '<option value="">Seleccione...</option>';
            data.forEach(c => {
                const option = document.createElement("option");
                option.value = c.confederacionid;
                option.text = c.nombre;
                if (seleccionado && c.confederacionid == seleccionado) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        });
}

function guardarPais() {
    const pais = {
        PaisID: document.getElementById("txtPaisID").value,
        Nombre: document.getElementById("txtNombre").value,
        CodigoFIFA: document.getElementById("txtCodigoFIFA").value,
        ConfederacionID: document.getElementById("selectConfederacion").value
    };

    fetch('/api/paises/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pais)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cerrarModal();
            listarPaises();
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => console.error("Error al guardar:", error));
}

function editarPais(id) {
    fetch(`/api/paises/buscar/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data) {
                document.getElementById("tituloModal").innerText = "Editar País";
                document.getElementById("txtPaisID").value = data.paisid;
                document.getElementById("txtNombre").value = data.nombre;
                document.getElementById("txtCodigoFIFA").value = data.codigofifa;
                cargarConfederaciones(data.confederacionid);
                mostrarModal();
            }
        });
}

function eliminarPais(id) {
    if (!confirm("¿Estás seguro de eliminar este país?")) return;

    fetch(`/api/paises/eliminar/${id}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                listarPaises();
            } else {
                alert("Error al eliminar: " + data.message);
            }
        });
}

function mostrarModal() {
    const modal = document.getElementById("modalPais");
    const content = document.getElementById("modalPaisContent");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    setTimeout(() => {
        content.classList.remove("scale-95", "opacity-0");
        content.classList.add("scale-100", "opacity-100");
    }, 10);
}

function cerrarModal() {
    const modal = document.getElementById("modalPais");
    const content = document.getElementById("modalPaisContent");
    content.classList.remove("scale-100", "opacity-100");
    content.classList.add("scale-95", "opacity-0");
    setTimeout(() => {
        modal.classList.remove("flex");
        modal.classList.add("hidden");
    }, 300);
}

document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') cerrarModal();
});