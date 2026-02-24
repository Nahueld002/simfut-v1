document.addEventListener("DOMContentLoaded", function () {
    listarEquipos();
    cargarPaises(); 

    let timeout = null;
    document.getElementById("txtBuscar").addEventListener("input", function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => listarEquipos(this.value), 300);
    });

    document.getElementById("formEquipo").addEventListener("submit", function (e) {
        e.preventDefault();
        guardarEquipo();
    });
});

function listarEquipos(filtro = "") {
    let url = '/api/equipos/listar';
    if (filtro) url += `?nombre=${encodeURIComponent(filtro)}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("#tablaEquipos tbody");
            tbody.innerHTML = "";

            if (data.data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="p-4 text-center text-gray-500">No se encontraron equipos.</td></tr>`;
                return;
            }

            data.data.forEach((item, index) => {
                const rowClass = index % 2 === 0 ? 'bg-gray-800/30' : 'bg-transparent';
                
                let estadoColor = 'text-gray-400 bg-gray-400/10';
                if (item.estado === 'Activo') estadoColor = 'text-green-400 bg-green-400/10';
                else if (item.estado === 'Desaparecido') estadoColor = 'text-red-400 bg-red-400/10';
                else if (item.estado === 'Suspendido') estadoColor = 'text-yellow-400 bg-yellow-400/10';

                const eloFormat = item.elo ? parseFloat(item.elo).toFixed(2) : '1000.00';

                const tr = document.createElement("tr");
                tr.className = `hover:bg-gray-700/50 transition-colors ${rowClass}`;
                
                tr.innerHTML = `
                    <td class="p-4 font-bold text-white">${item.nombre}</td>
                    
                    <td class="p-4 font-mono text-gray-400 text-xs">${item.codigoequipo || '-'}</td>
                    
                    <td class="p-4 text-gray-300">
                        <div class="font-medium text-gray-200">${item.ciudad}</div>
                        <div class="text-xs text-gray-500">${item.region}</div>
                    </td>
                    
                    <td class="p-4 text-gray-300">${item.aniofundacion || '-'}</td>
                    
                    <td class="p-4 font-mono text-blue-300 font-bold">${eloFormat}</td>
                    
                    <td class="p-4 text-gray-300 text-xs uppercase tracking-wide">${item.tipoequipo || 'Club'}</td>
                    
                    <td class="p-4">
                        <span class="px-2 py-1 rounded text-xs font-semibold ${estadoColor}">${item.estado}</span>
                    </td>
                    
                    <td class="p-4 text-center">
                        <div class="flex items-center justify-center gap-2">
                            <button onclick="editarEquipo(${item.equipoid})" class="p-1.5 bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white rounded transition-all" title="Editar">
                                <i data-lucide="edit-2" class="w-4 h-4"></i>
                            </button>
                            <button onclick="eliminarEquipo(${item.equipoid})" class="p-1.5 bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white rounded transition-all" title="Eliminar">
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
            select.innerHTML = '<option value="">Seleccione País...</option>';
            data.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.paisid;
                opt.text = p.nombre;
                if (seleccionado && p.paisid == seleccionado) opt.selected = true;
                select.appendChild(opt);
            });
        });
}

function cargarCiudadesPorPais(paisId = null, ciudadSeleccionada = null) {
    if (!paisId) paisId = document.getElementById("selectPais").value;
    
    const selectCiudad = document.getElementById("selectCiudad");
    const txtRegion = document.getElementById("txtRegionNombre");
    const hdnRegion = document.getElementById("hdnRegionID");

    selectCiudad.innerHTML = '<option value="">Cargando...</option>';
    txtRegion.value = "";
    hdnRegion.value = "";
    selectCiudad.disabled = true;

    if (!paisId) {
        selectCiudad.innerHTML = '<option value="">Seleccione País primero</option>';
        return;
    }

    fetch(`/api/general/ciudades/pais/${paisId}`)
        .then(res => res.json())
        .then(data => {
            selectCiudad.innerHTML = '<option value="">Seleccione Ciudad...</option>';
            selectCiudad.disabled = false;
            
            data.forEach(c => {
                const opt = document.createElement("option");
                opt.value = c.ciudadid;
                opt.text = c.nombre;
                opt.setAttribute("data-region-id", c.regionid);
                opt.setAttribute("data-region-nombre", c.region_nombre);
                
                if (ciudadSeleccionada && c.ciudadid == ciudadSeleccionada) {
                    opt.selected = true;
                    txtRegion.value = c.region_nombre;
                    hdnRegion.value = c.regionid;
                }
                selectCiudad.appendChild(opt);
            });
        });
}

function autoCompletarRegion() {
    const selectCiudad = document.getElementById("selectCiudad");
    const selectedOption = selectCiudad.options[selectCiudad.selectedIndex];
    
    const txtRegion = document.getElementById("txtRegionNombre");
    const hdnRegion = document.getElementById("hdnRegionID");

    if (selectedOption && selectedOption.value) {
        txtRegion.value = selectedOption.getAttribute("data-region-nombre");
        hdnRegion.value = selectedOption.getAttribute("data-region-id");
    } else {
        txtRegion.value = "";
        hdnRegion.value = "";
    }
}


function abrirModalEquipo() {
    document.getElementById("tituloModal").innerText = "Nuevo Equipo";
    document.getElementById("txtEquipoID").value = "0";
    document.getElementById("formEquipo").reset();
    document.getElementById("txtELO").value = "1000";
    document.getElementById("selectEstado").value = "Activo";
    document.getElementById("selectTipo").value = "Club";
    document.getElementById("selectPais").value = "";
    document.getElementById("selectCiudad").innerHTML = '<option value="">Seleccione País primero</option>';
    document.getElementById("selectCiudad").disabled = true;
    document.getElementById("txtRegionNombre").value = "";
    document.getElementById("hdnRegionID").value = "";
    mostrarModal();
}

function guardarEquipo() {
    const data = {
        EquipoID: document.getElementById("txtEquipoID").value,
        Nombre: document.getElementById("txtNombre").value,
        Codigo: document.getElementById("txtCodigo").value,
        Anio: document.getElementById("txtAnio").value,
        CiudadID: document.getElementById("selectCiudad").value,
        RegionID: document.getElementById("hdnRegionID").value,
        ELO: document.getElementById("txtELO").value,
        Tipo: document.getElementById("selectTipo").value,
        Estado: document.getElementById("selectEstado").value
    };

    fetch('/api/equipos/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            cerrarModal();
            listarEquipos();
        } else {
            alert("Error: " + data.message);
        }
    });
}

function editarEquipo(id) {
    fetch(`/api/equipos/buscar/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data) {
                document.getElementById("tituloModal").innerText = "Editar Equipo";
                document.getElementById("txtEquipoID").value = data.equipoid;
                document.getElementById("txtNombre").value = data.nombre;
                document.getElementById("txtCodigo").value = data.codigoequipo;
                document.getElementById("txtAnio").value = data.aniofundacion;
                
                document.getElementById("txtELO").value = data.elo;
                document.getElementById("selectTipo").value = data.tipoequipo || 'Club';
                document.getElementById("selectEstado").value = data.estado || 'Activo';
                
                document.getElementById("selectPais").value = data.paisid;
                setTimeout(() => {
                    cargarCiudadesPorPais(data.paisid, data.ciudadid);
                }, 50);
                
                mostrarModal();
            }
        });
}

function eliminarEquipo(id) {
    if (!confirm("¿Eliminar este equipo?")) return;
    fetch(`/api/equipos/eliminar/${id}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                listarEquipos();
            } else {
                alert("Error: " + data.message);
            }
        });
}

function mostrarModal() {
    const modal = document.getElementById("modalEquipo");
    const content = document.getElementById("modalEquipoContent");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    setTimeout(() => {
        content.classList.remove("scale-95", "opacity-0");
        content.classList.add("scale-100", "opacity-100");
    }, 10);
}

function cerrarModal() {
    const modal = document.getElementById("modalEquipo");
    const content = document.getElementById("modalEquipoContent");
    content.classList.remove("scale-100", "opacity-100");
    content.classList.add("scale-95", "opacity-0");
    setTimeout(() => {
        modal.classList.remove("flex");
        modal.classList.add("hidden");
    }, 300);
}