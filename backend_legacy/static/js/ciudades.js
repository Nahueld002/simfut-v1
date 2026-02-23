document.addEventListener("DOMContentLoaded", function () {
    listarCiudades();
    cargarPaises();

    document.getElementById("txtBuscar").addEventListener("keyup", function() {
        const value = this.value.toLowerCase();
        const rows = document.querySelectorAll("#tablaCiudades tbody tr");
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(value) ? "" : "none";
        });
    });

    document.getElementById("formCiudad").addEventListener("submit", function (e) {
        e.preventDefault();
        guardarCiudad();
    });
});

function listarCiudades() {
    fetch('/api/ciudades/listar')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("#tablaCiudades tbody");
            tbody.innerHTML = "";

            if (data.data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-gray-500">No hay registros.</td></tr>`;
                return;
            }

            data.data.forEach((item, index) => {
                const rowClass = index % 2 === 0 ? 'bg-gray-800/30' : 'bg-transparent';
                const capitalIcon = item.escapital ? `<i data-lucide="star" class="w-4 h-4 text-yellow-400 inline"></i>` : `<span class="text-gray-600">-</span>`;
                
                const tr = document.createElement("tr");
                tr.className = `hover:bg-gray-700/50 transition-colors ${rowClass}`;
                tr.innerHTML = `
                    <td class="p-4 font-bold text-white">${item.nombre}</td>
                    <td class="p-4 text-gray-300">${item.region}</td>
                    <td class="p-4 text-gray-400 text-sm">${item.pais}</td>
                    <td class="p-4 text-center">${capitalIcon}</td>
                    <td class="p-4 text-center">
                        <div class="flex items-center justify-center gap-2">
                            <button onclick="editarCiudad(${item.ciudadid})" class="p-1.5 bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white rounded transition-all">
                                <i data-lucide="edit-2" class="w-4 h-4"></i>
                            </button>
                            <button onclick="eliminarCiudad(${item.ciudadid})" class="p-1.5 bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white rounded transition-all">
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

function cargarRegionesPorPais(paisId = null, regionSeleccionada = null) {
    if (!paisId) paisId = document.getElementById("selectPais").value;
    
    const selectRegion = document.getElementById("selectRegion");
    selectRegion.innerHTML = '<option value="">Cargando...</option>';
    selectRegion.disabled = true;

    if (!paisId) {
        selectRegion.innerHTML = '<option value="">Seleccione País primero</option>';
        return;
    }

    fetch(`/api/general/regiones/pais/${paisId}`)
        .then(res => res.json())
        .then(data => {
            selectRegion.innerHTML = '<option value="">Seleccione...</option>';
            selectRegion.disabled = false;
            
            data.forEach(r => {
                const opt = document.createElement("option");
                opt.value = r.regionid;
                opt.text = r.nombre;
                if (regionSeleccionada && r.regionid == regionSeleccionada) opt.selected = true;
                selectRegion.appendChild(opt);
            });
        });
}

function abrirModalCiudad() {
    document.getElementById("tituloModal").innerText = "Nueva Ciudad";
    document.getElementById("txtCiudadID").value = "0";
    document.getElementById("txtNombre").value = "";
    document.getElementById("selectPais").value = "";
    document.getElementById("selectRegion").innerHTML = '<option value="">Seleccione País primero</option>';
    document.getElementById("selectRegion").disabled = true;
    document.getElementById("chkCapital").checked = false;
    mostrarModal();
}

function guardarCiudad() {
    const data = {
        CiudadID: document.getElementById("txtCiudadID").value,
        Nombre: document.getElementById("txtNombre").value,
        RegionID: document.getElementById("selectRegion").value,
        EsCapital: document.getElementById("chkCapital").checked
    };

    fetch('/api/ciudades/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            cerrarModal();
            listarCiudades();
        } else {
            alert("Error: " + data.message);
        }
    });
}

function editarCiudad(id) {
    fetch(`/api/ciudades/buscar/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data) {
                document.getElementById("tituloModal").innerText = "Editar Ciudad";
                document.getElementById("txtCiudadID").value = data.ciudadid;
                document.getElementById("txtNombre").value = data.nombre;
                document.getElementById("chkCapital").checked = data.escapital;
                
                document.getElementById("selectPais").value = data.paisid;
                setTimeout(() => {
                    cargarRegionesPorPais(data.paisid, data.regionid);
                }, 50);
                
                mostrarModal();
            }
        });
}

function eliminarCiudad(id) {
    if (!confirm("¿Eliminar esta ciudad?")) return;
    
    fetch(`/api/ciudades/eliminar/${id}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                listarCiudades();
            } else {
                alert("Error: " + data.message);
            }
        });
}

function mostrarModal() {
    const modal = document.getElementById("modalCiudad");
    const content = document.getElementById("modalCiudadContent");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    setTimeout(() => {
        content.classList.remove("scale-95", "opacity-0");
        content.classList.add("scale-100", "opacity-100");
    }, 10);
}

function cerrarModal() {
    const modal = document.getElementById("modalCiudad");
    const content = document.getElementById("modalCiudadContent");
    content.classList.remove("scale-100", "opacity-100");
    content.classList.add("scale-95", "opacity-0");
    setTimeout(() => {
        modal.classList.remove("flex");
        modal.classList.add("hidden");
    }, 300);
}