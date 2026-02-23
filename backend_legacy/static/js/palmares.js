document.addEventListener("DOMContentLoaded", function () {
    cargarPalmares();
});

function cargarPalmares() {
    const divRanking = document.getElementById("contenedorRanking");
    const tbodyHistorial = document.getElementById("tablaHistorial");

    fetch('/api/palmares/resumen')
        .then(r => r.json())
        .then(data => {
            renderizarRanking(data.ranking, divRanking);
            renderizarHistorial(data.historial, tbodyHistorial);
            lucide.createIcons();
        })
        .catch(err => console.error("Error cargando palmarés:", err));
}

function renderizarRanking(datos, contenedor) {
    contenedor.innerHTML = "";
    
    if (!datos || datos.length === 0) {
        contenedor.innerHTML = '<p class="text-gray-500 text-center text-sm">Sin datos aún.</p>';
        return;
    }

    const lider = datos[0];
    const topCard = document.createElement("div");
    topCard.className = "bg-gradient-to-r from-yellow-900/40 to-gray-800 p-4 rounded-lg border border-yellow-500/30 mb-6 flex items-center justify-between";
    topCard.innerHTML = `
        <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-yellow-500 flex items-center justify-center text-black font-bold text-lg shadow-lg shadow-yellow-500/20">
                1º
            </div>
            <div>
                <p class="text-yellow-400 text-xs font-bold uppercase tracking-wider">Líder Histórico</p>
                <p class="text-white font-bold text-lg">${lider.nombre}</p>
            </div>
        </div>
        <div class="text-center">
            <p class="text-2xl font-bold text-white">${lider.total_titulos}</p>
            <p class="text-[10px] text-gray-400 uppercase">Títulos</p>
        </div>
    `;
    contenedor.appendChild(topCard);

    datos.slice(1).forEach((team, index) => {
        const row = document.createElement("div");
        row.className = "flex items-center justify-between p-3 hover:bg-gray-700/30 rounded-lg transition-colors border-b border-gray-700/50 last:border-0";
        
        let rankColor = "bg-gray-700 text-gray-300"; 
        if (index === 0) rankColor = "bg-gray-400 text-gray-900"; 
        if (index === 1) rankColor = "bg-orange-700 text-orange-100";

        row.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="w-6 h-6 rounded text-xs font-bold flex items-center justify-center ${rankColor}">
                    ${index + 2}
                </span>
                <span class="text-gray-200 font-medium text-sm">${team.nombre}</span>
            </div>
            <span class="font-bold text-white">${team.total_titulos} <i data-lucide="trophy" class="w-3 h-3 inline text-yellow-500 ml-1"></i></span>
        `;
        contenedor.appendChild(row);
    });
}

function renderizarHistorial(datos, tbody) {
    tbody.innerHTML = "";
    
    if (!datos || datos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="p-6 text-center text-gray-500">No hay campeones registrados.</td></tr>';
        return;
    }

    datos.forEach(row => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-gray-700/30 transition-colors border-b border-gray-700/50";
        tr.innerHTML = `
            <td class="p-4 text-center font-bold text-blue-400">${row.aniotitulo}</td>
            <td class="p-4 text-gray-300">${row.torneo}</td>
            <td class="p-4">
                <span class="font-bold text-yellow-400 flex items-center gap-2">
                    <i data-lucide="trophy" class="w-4 h-4"></i> ${row.campeon}
                </span>
            </td>
            <td class="p-4 text-right">
                <span class="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded border border-gray-600">
                    ${row.categoria || 'General'}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}