document.addEventListener("DOMContentLoaded", function () {
    listarRegiones();
    cargarPaises();

    document.getElementById("formRegion").addEventListener("submit", function (e) {
        e.preventDefault();
        guardarRegion();
    });
});

function listarRegiones() {
    fetch('/api/regiones/listar')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("#tablaRegiones tbody");
            tbody.innerHTML = "";

            if (data.data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-gray-500">No hay registros.</td></tr>`;
                return;
            }

            data.data.forEach((item, index) => {
                const rowClass = index % 2 === 0 ? 'bg-gray-800/30' : 'bg-transparent';
                
                const tr = document.createElement("tr");
                tr.className = `hover:bg-gray-700/50 transition-colors ${rowClass}`;
                tr.innerHTML = `
                    <td class="p-4 font-bold text-white">${item.nombre}</td>
                    <td class="p-4 text-gray-300 text-sm">${item.tiporegion}</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded bg-gray-700 text-gray-300 text-xs font-semibold">
                            ${item.nombrepais}
                        </span>
                    </td>
                    <td class="p-4 text-center">
                        <div class="flex items-center justify-center gap-2">
                            <button onclick="editarRegion(${item.regionid})" class="p-1.5 bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white rounded transition-all">
                                <i data-lucide="edit-2" class="w-4 h-4"></i>
                            </button>
                            <button onclick="eliminarRegion(${item.regionid})" class="p-1.5 bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white rounded transition-all">
                                <i data-lucide="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            lucide.createIcons();
        });
}

function cargarPaises(seleccionado = null) {
    fetch('/api/general/paises')
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById("selectPais");
            select.innerHTML = '<option value="">Seleccione...</option>';
            data.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.paisid;
                opt.text = p.nombre;
                if (seleccionado && p.paisid == seleccionado) opt.selected = true;
                select.appendChild(opt);
            });
        });
}

function abrirModalRegion() {
    document.getElementById("tituloModal").innerText = "Nueva Región";
    document.getElementById("txtRegionID").value = "0";
    document.getElementById("txtNombre").value = "";
    document.getElementById("txtTipo").value = "Departamento";
    document.getElementById("selectPais").value = "";
    mostrarModal();
}

function guardarRegion() {
    const data = {
        RegionID: document.getElementById("txtRegionID").value,
        Nombre: document.getElementById("txtNombre").value,
        TipoRegion: document.getElementById("txtTipo").value,
        PaisID: document.getElementById("selectPais").value
    };

    fetch('/api/regiones/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            cerrarModal();
            listarRegiones();
        } else {
            alert("Error: " + data.message);
        }
    });
}

function editarRegion(id) {
    fetch(`/api/regiones/buscar/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data) {
                document.getElementById("tituloModal").innerText = "Editar Región";
                document.getElementById("txtRegionID").value = data.regionid;
                document.getElementById("txtNombre").value = data.nombre;
                document.getElementById("txtTipo").value = data.tiporegion;
                cargarPaises(data.paisid);
                mostrarModal();
            }
        });
}

function eliminarRegion(id) {
    if (!confirm("¿Eliminar esta región?")) return;
    
    fetch(`/api/regiones/eliminar/${id}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                listarRegiones();
            } else {
                alert("Error: " + data.message);
            }
        });
}

function mostrarModal() {
    const modal = document.getElementById("modalRegion");
    const content = document.getElementById("modalRegionContent");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    setTimeout(() => {
        content.classList.remove("scale-95", "opacity-0");
        content.classList.add("scale-100", "opacity-100");
    }, 10);
}

function cerrarModal() {
    const modal = document.getElementById("modalRegion");
    const content = document.getElementById("modalRegionContent");
    content.classList.remove("scale-100", "opacity-100");
    content.classList.add("scale-95", "opacity-0");
    setTimeout(() => {
        modal.classList.remove("flex");
        modal.classList.add("hidden");
    }, 300);
}