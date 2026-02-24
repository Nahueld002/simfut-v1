document.addEventListener("DOMContentLoaded", function () {
    listarConfederaciones();

    document.getElementById("formConf").addEventListener("submit", function (e) {
        e.preventDefault();
        guardarConfederacion();
    });
});

function listarConfederaciones() {
    fetch('/api/confederaciones/listar')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector("#tablaConfederaciones tbody");
            tbody.innerHTML = "";

            if (data.data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="3" class="p-4 text-center text-gray-500">No hay registros.</td></tr>`;
                return;
            }

            data.data.forEach((item, index) => {
                const rowClass = index % 2 === 0 ? 'bg-gray-800/30' : 'bg-transparent';
                
                const tr = document.createElement("tr");
                tr.className = `hover:bg-gray-700/50 transition-colors ${rowClass}`;
                tr.innerHTML = `
                    <td class="p-4 font-mono text-gray-500 text-xs">#${item.confederacionid}</td>
                    <td class="p-4 font-bold text-white">${item.nombre}</td>
                    <td class="p-4 text-center">
                        <div class="flex items-center justify-center gap-2">
                            <button onclick="editarConf(${item.confederacionid})" class="p-1.5 bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white rounded transition-all">
                                <i data-lucide="edit-2" class="w-4 h-4"></i>
                            </button>
                            <button onclick="eliminarConf(${item.confederacionid})" class="p-1.5 bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white rounded transition-all">
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

function abrirModalConf() {
    document.getElementById("tituloModal").innerText = "Nueva Confederación";
    document.getElementById("txtConfID").value = "0";
    document.getElementById("txtNombre").value = "";
    mostrarModal();
}

function guardarConfederacion() {
    const data = {
        ConfederacionID: document.getElementById("txtConfID").value,
        Nombre: document.getElementById("txtNombre").value
    };

    fetch('/api/confederaciones/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            cerrarModal();
            listarConfederaciones();
        } else {
            alert("Error: " + data.message);
        }
    });
}

function editarConf(id) {
    fetch(`/api/confederaciones/buscar/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data) {
                document.getElementById("tituloModal").innerText = "Editar Confederación";
                document.getElementById("txtConfID").value = data.confederacionid;
                document.getElementById("txtNombre").value = data.nombre;
                mostrarModal();
            }
        });
}

function eliminarConf(id) {
    if (!confirm("¿Eliminar esta confederación?")) return;
    
    fetch(`/api/confederaciones/eliminar/${id}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                listarConfederaciones();
            } else {
                alert("Error: " + data.message);
            }
        });
}

function mostrarModal() {
    const modal = document.getElementById("modalConf");
    const content = document.getElementById("modalConfContent");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    setTimeout(() => {
        content.classList.remove("scale-95", "opacity-0");
        content.classList.add("scale-100", "opacity-100");
    }, 10);
    setTimeout(() => document.getElementById("txtNombre").focus(), 100);
}

function cerrarModal() {
    const modal = document.getElementById("modalConf");
    const content = document.getElementById("modalConfContent");
    content.classList.remove("scale-100", "opacity-100");
    content.classList.add("scale-95", "opacity-0");
    setTimeout(() => {
        modal.classList.remove("flex");
        modal.classList.add("hidden");
    }, 300);
}