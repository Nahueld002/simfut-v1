document.addEventListener("DOMContentLoaded", function () {
    cargarConfederaciones();
});

function cargarConfederaciones() {
    const grid = document.getElementById("gridConfederaciones");
    if(!grid) return;

    grid.innerHTML = '<div class="text-gray-500 col-span-full text-center py-4">...</div>';

    fetch('/api/general/confederaciones')
        .then(res => res.json())
        .then(data => {
            grid.innerHTML = "";
            data.forEach(c => {
                const card = document.createElement("div");
                card.className = "card-confederacion bg-gray-900 border border-gray-700 hover:border-blue-500 hover:bg-gray-800 p-2 rounded-lg cursor-pointer transition-all flex flex-col items-center justify-center gap-1 group shadow-sm";
                card.onclick = () => seleccionarConfederacion(c.confederacionid, card);
                const rutaImagen = `/static/img/confederacion/${c.confederacionid}.png`;
                
                card.innerHTML = `
                    <div class="p-1.5 rounded-full bg-gray-800 group-hover:bg-blue-900/30 transition-colors pointer-events-none">
                        <img src="${rutaImagen}" alt="${c.nombre}" class="w-8 h-8 object-contain drop-shadow-sm"
                             onerror="this.onerror=null; this.src=''; this.parentElement.innerHTML='<i data-lucide=globe class=\'w-5 h-5 text-gray-500\'></i>'">
                    </div>
                    <span class="text-[10px] font-bold text-gray-400 group-hover:text-white text-center pointer-events-none uppercase tracking-wide truncate w-full">${c.nombre}</span>
                `;
                grid.appendChild(card);
            });
            lucide.createIcons(); 
        });
}

function seleccionarConfederacion(id, cardElement) {
    document.getElementById("hdnConfederacionID").value = id;
    const todas = document.querySelectorAll('.card-confederacion');
    todas.forEach(c => {
        c.classList.remove('ring-2', 'ring-blue-500', 'bg-gray-700');
        c.classList.add('bg-gray-900', 'border-gray-700');
    });
    cardElement.classList.remove('bg-gray-900', 'border-gray-700');
    cardElement.classList.add('ring-2', 'ring-blue-500', 'bg-gray-700');

    const placeholder = document.getElementById("placeholderPais");
    const contenedor = document.getElementById("contenedorFiltroPais");
    if(placeholder && contenedor) {
        placeholder.classList.add("hidden"); 
        contenedor.classList.remove("opacity-50", "blur-[2px]");
        contenedor.classList.add("opacity-100", "blur-0"); 
    }
    cargarPaises();
}


function cargarPaises() {
    const confId = document.getElementById("hdnConfederacionID").value; 
    const selectPais = document.getElementById("selectPais");
    const btnInter = document.getElementById("btnInternacional");
    
    document.getElementById("contenedorTorneos").classList.add("hidden");
    document.getElementById("detalleTorneo").classList.add("hidden");
    selectPais.innerHTML = '<option value="">Cargando...</option>';
    
    if (!confId) return; 

    btnInter.disabled = false;
    btnInter.classList.remove("opacity-50", "cursor-not-allowed");

    fetch(`/api/general/paises/confederacion/${confId}`)
        .then(res => res.json())
        .then(data => {
            selectPais.innerHTML = '<option value="">Seleccione País...</option>';
            selectPais.disabled = false;
            data.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.paisid;
                opt.text = p.nombre;
                selectPais.appendChild(opt);
            });
        });
}


function cargarTorneos() {
    const paisId = document.getElementById("selectPais").value;
    const grid = document.getElementById("gridTorneos");
    const container = document.getElementById("contenedorTorneos");
    document.getElementById("detalleTorneo").classList.add("hidden");

    if (!paisId) { container.classList.add("hidden"); return; }

    fetch(`/api/torneos/por_pais/${paisId}`)
        .then(res => res.json())
        .then(data => {
            grid.innerHTML = "";
            container.classList.remove("hidden");
            if (data.length === 0) {
                grid.innerHTML = `<p class="text-gray-500 col-span-3">No se encontraron torneos activos.</p>`;
                return;
            }
            data.forEach(t => {
                const card = document.createElement("div");
                card.className = "bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-blue-500 cursor-pointer transition-all hover:shadow-lg hover:shadow-blue-900/20 group";
                card.onclick = () => seleccionarTorneo(t.torneoid, t.nombre, t.categoria || 'Sin categoría');
                card.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div class="p-2 bg-gray-700 rounded-full text-blue-400 group-hover:text-white group-hover:bg-blue-600 transition-colors">
                            <i data-lucide="trophy" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h4 class="font-bold text-white text-sm">${t.nombre}</h4>
                            <p class="text-xs text-gray-400">${t.tipotorneo}</p>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
            lucide.createIcons();
        });
}

function seleccionarTorneo(id, nombre, categoria) {
    document.getElementById("detalleTorneo").classList.remove("hidden");
    document.getElementById("tituloTorneo").innerText = nombre;
    document.getElementById("subtituloTorneo").innerText = categoria;
    document.getElementById("hdnTorneoID").value = id;
    document.getElementById("hdnTorneoNombre").value = nombre;
    cambiarTab('equipos'); 
    document.getElementById("detalleTorneo").scrollIntoView({ behavior: 'smooth', block: 'start' });
}


function actualizarDetalles() {
    const tabEquipos = document.getElementById("tab-equipos");
    const tabPartidos = document.getElementById("tab-partidos");
    
    if (tabEquipos.classList.contains("border-blue-500")) {
        cargarEquiposParticipantes();
    } else if (tabPartidos.classList.contains("border-blue-500")) {
        cargarPartidos();
    } else {
        cargarTablaPosiciones();
    }
}

function cambiarTab(tabName) {
    const vistas = ['equipos', 'partidos', 'tabla'];
    
    vistas.forEach(v => {
        const div = document.getElementById(`vista-${v}`);
        const btn = document.getElementById(`tab-${v}`);
        
        if (v === tabName) {
            div.classList.remove("hidden");
            btn.classList.add("border-b-2", "border-blue-500", "text-blue-400", "bg-gray-800");
            btn.classList.remove("text-gray-400");
            if(v === 'equipos') cargarEquiposParticipantes();
            if(v === 'partidos') cargarPartidos();
            if(v === 'tabla') cargarTablaPosiciones();
            
        } else {
            div.classList.add("hidden");
            btn.classList.remove("border-b-2", "border-blue-500", "text-blue-400", "bg-gray-800");
            btn.classList.add("text-gray-400");
        }
    });
}


function cargarEquiposParticipantes() {
    const torneoId = document.getElementById("hdnTorneoID").value;
    const anio = document.getElementById("selectAnio").value;
    const grid = document.getElementById("gridEquipos");
    const contador = document.getElementById("contadorEquipos");

    grid.innerHTML = '<p class="text-gray-500">Cargando...</p>';

    fetch(`/api/torneos/equipos_participantes?torneo_id=${torneoId}&anio=${anio}`)
        .then(res => res.json())
        .then(res => {
            const data = res.data;
            grid.innerHTML = "";
            contador.innerText = `${data.length} equipos`;
            if (data.length === 0) {
                grid.innerHTML = `<p class="col-span-4 text-gray-500 italic">No hay equipos inscritos en ${anio}.</p>`;
                return;
            }
            data.forEach(e => {
                const div = document.createElement("div");
                div.className = "bg-gray-700/50 p-3 rounded border border-gray-600 flex items-center gap-2";
                div.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-xs font-bold text-white">
                        ${e.codigoequipo ? e.codigoequipo.substring(0,2) : 'EQ'}
                    </div>
                    <div class="truncate">
                        <p class="text-sm font-medium text-white truncate" title="${e.nombre}">${e.nombre}</p>
                        <p class="text-xs text-gray-400 truncate">${e.ciudad || ''}</p>
                    </div>
                `;
                grid.appendChild(div);
            });
        });
}


function cargarPartidos() {
    const torneoId = document.getElementById("hdnTorneoID").value;
    const anio = document.getElementById("selectAnio").value;
    const container = document.getElementById("contenedorFechas");
    
    container.innerHTML = '<div class="text-center py-8"><i data-lucide="loader-2" class="w-8 h-8 animate-spin mx-auto text-blue-500"></i></div>';
    lucide.createIcons();

    fetch(`/api/partidos/listar?torneo_id=${torneoId}&anio=${anio}`)
        .then(r => r.json())
        .then(res => {
            const partidos = res.data;
            container.innerHTML = "";

            if (!partidos || partidos.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-center py-8">No hay partidos registrados para este año.</p>';
                return;
            }

            const partidosPorFecha = {};
            partidos.forEach(p => {
                if (!partidosPorFecha[p.nrofecha]) partidosPorFecha[p.nrofecha] = [];
                partidosPorFecha[p.nrofecha].push(p);
            });

            for (const [fecha, matches] of Object.entries(partidosPorFecha)) {
                const fechaDiv = document.createElement("div");
                fechaDiv.className = "mb-6";
                fechaDiv.innerHTML = `
                    <h3 class="text-lg font-bold text-blue-400 mb-3 border-b border-gray-700 pb-1">Fecha ${fecha}</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${matches.map(p => renderCardPartido(p)).join('')}
                    </div>
                `;
                container.appendChild(fechaDiv);
            }
            lucide.createIcons();
        });
}

function renderCardPartido(p) {
    const finalizado = p.estado === 'Finalizado';
    const bgClass = finalizado ? 'bg-gray-800 border-gray-700' : 'bg-gray-800 border-l-4 border-l-yellow-500 border-gray-700';
    const marcador = finalizado 
        ? `<span class="text-2xl font-bold text-white tracking-widest">${p.goleslocal} - ${p.golesvisitante}</span>`
        : `<span class="text-sm font-bold text-yellow-500 bg-yellow-500/10 px-2 py-1 rounded">VS</span>`;

    const botones = finalizado
        ? `<button onclick="abrirModalEditar(${p.partidoid}, '${p.local}', '${p.visitante}', ${p.goleslocal}, ${p.golesvisitante})" class="text-xs text-gray-500 hover:text-blue-400 flex items-center gap-1"><i data-lucide="edit-2" class="w-3 h-3"></i> Editar</button>`
        : `<div class="flex gap-2 w-full mt-3">
             <button onclick="simularUno(${p.partidoid})" class="flex-1 bg-green-600 hover:bg-green-700 text-white text-xs font-bold py-1.5 rounded flex justify-center items-center gap-1 transition-colors">
                <i data-lucide="zap" class="w-3 h-3"></i> Simular
             </button>
             <button onclick="abrirModalEditar(${p.partidoid}, '${p.local}', '${p.visitante}', 0, 0)" class="flex-1 bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs font-bold py-1.5 rounded flex justify-center items-center gap-1">
                <i data-lucide="edit" class="w-3 h-3"></i> Manual
             </button>
           </div>`;

    return `
        <div class="card p-4 rounded-lg border ${bgClass} shadow-sm relative group hover:border-blue-500/30 transition-all">
            <div class="flex justify-between items-center mb-2">
                <span class="text-xs text-gray-500">${p.grupo || 'Liga'}</span>
                ${finalizado ? '<i data-lucide="check-circle" class="w-4 h-4 text-green-500"></i>' : ''}
            </div>
            <div class="flex justify-between items-center gap-2">
                <div class="text-center w-1/3">
                    <div class="font-bold text-white truncate" title="${p.local}">${p.local}</div>
                </div>
                <div class="text-center w-1/3 flex justify-center">${marcador}</div>
                <div class="text-center w-1/3">
                    <div class="font-bold text-white truncate" title="${p.visitante}">${p.visitante}</div>
                </div>
            </div>
            <div class="flex justify-center mt-2">${botones}</div>
        </div>
    `;
}

function simularUno(id) {
    fetch(`/api/partidos/simular_uno/${id}`, { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        if(data.success) cargarPartidos(); 
        else alert("Error: " + data.message);
    });
}

function abrirModalEditar(id, local, visita, gl, gv) {
    document.getElementById("modalEditar").classList.remove("hidden");
    document.getElementById("modalEditar").classList.add("flex");
    document.getElementById("hdnPartidoID").value = id;
    document.getElementById("lblLocal").innerText = local;
    document.getElementById("lblVisita").innerText = visita;
    document.getElementById("txtGolesLocal").value = gl;
    document.getElementById("txtGolesVisita").value = gv;
}

function cerrarModal() {
    document.getElementById("modalEditar").classList.add("hidden");
    document.getElementById("modalEditar").classList.remove("flex");
}

function guardarResultadoManual() {
    const id = document.getElementById("hdnPartidoID").value;
    const gl = document.getElementById("txtGolesLocal").value;
    const gv = document.getElementById("txtGolesVisita").value;

    fetch('/api/partidos/guardar_resultado', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ partido_id: id, goles_local: gl, goles_visita: gv })
    }).then(r => r.json()).then(data => {
        if(data.success) { 
            cerrarModal(); 
            cargarPartidos(); 
        } else {
            alert("Error: " + data.message);
        }
    });
}

function cargarTablaPosiciones() {
    const torneoId = document.getElementById("hdnTorneoID").value;
    const anio = document.getElementById("selectAnio").value;
    const contenedor = document.getElementById("contenedorTablasPosiciones");
    contenedor.innerHTML = '<div class="text-center p-6"><i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto text-blue-500"></i></div>';
    lucide.createIcons();

    fetch(`/api/torneos/posiciones?torneo_id=${torneoId}&anio=${anio}`)
        .then(r => r.json())
        .then(res => renderizarTablasDinamicas(res.data, "contenedorTablasPosiciones"));
}

function simularFechas() {
    const nombre = document.getElementById("hdnTorneoNombre").value;
    const anio = document.getElementById("selectAnio").value;
    const btn = document.getElementById("btnSimular");

    if (!confirm(`¿Simular todos los partidos restantes de "${nombre}"?`)) return;

    btn.disabled = true;
    btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Simulando...`;
    lucide.createIcons();

    fetch('/api/torneos/simular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre: nombre, anio: parseInt(anio) })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) cargarTablaPosiciones();
        else alert("Error: " + data.message);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="play" class="w-4 h-4"></i> Simular Todo Restante`;
        lucide.createIcons();
    });
}

function generarFixture() {
    const torneoId = document.getElementById("hdnTorneoID").value;
    const anio = document.getElementById("selectAnio").value;
    const nombreTorneo = document.getElementById("tituloTorneo").innerText;
    if (!torneoId) {
        alert("Error: No se ha seleccionado un torneo.");
        return;
    }

    if (!confirm(`⚠️ ATENCIÓN ⚠️\n\nEstás a punto de generar el fixture para:\n» ${nombreTorneo} (${anio})\n\nSi ya existen partidos cargados para este año, SE BORRARÁN y se reemplazarán por nuevos.\n\n¿Deseas continuar?`)) {
        return;
    }

    // Feedback visual de carga (Spinner)
    const container = document.getElementById("contenedorFechas");
    container.innerHTML = `
        <div class="text-center py-12 bg-gray-800/50 rounded-xl border border-gray-700 border-dashed">
            <i data-lucide="loader-2" class="w-10 h-10 animate-spin mx-auto text-indigo-500 mb-3"></i>
            <h4 class="text-white font-bold">Generando Partidos...</h4>
            <p class="text-gray-400 text-sm mt-1">El motor está calculando los cruces y fechas.</p>
        </div>
    `;
    lucide.createIcons();

    fetch('/api/torneos/generar_fixture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            torneo_id: torneoId, 
            anio: anio 
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            cargarPartidos(); 
        } else {
            alert("❌ Ocurrió un error: " + data.message);
            cargarPartidos(); 
        }
    })
    .catch(err => {
        console.error(err);
        alert("Error de conexión con el servidor.");
        container.innerHTML = '<p class="text-red-500 text-center py-4">Error de conexión.</p>';
    });
}