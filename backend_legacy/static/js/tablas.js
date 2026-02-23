function renderizarTablasDinamicas(data, contenedorId) {
    const contenedor = document.getElementById(contenedorId);
    contenedor.innerHTML = "";

    if (!data || data.length === 0) {
        contenedor.innerHTML = `<div class="p-8 text-center text-gray-500 bg-gray-800 rounded-xl border border-gray-700">Aún no hay datos disponibles.</div>`;
        return;
    }

    const grupos = {};
    
    data.forEach(equipo => {
        let nombreGrupo = "Tabla General";
        
        if (equipo.grupo && equipo.grupo !== 'Único') {
            const fasePrefix = equipo.fase ? `${equipo.fase} - ` : '';
            nombreGrupo = `${fasePrefix}${equipo.grupo}`;
        } else if (equipo.fase && equipo.fase !== 'Regular') {
            nombreGrupo = equipo.fase;
        }

        if (!grupos[nombreGrupo]) {
            grupos[nombreGrupo] = [];
        }
        grupos[nombreGrupo].push(equipo);
    });

    const esUnicoGrupo = Object.keys(grupos).length === 1 && Object.keys(grupos)[0] === "Tabla General";

    for (const [nombre, equipos] of Object.entries(grupos)) {
        
        const section = document.createElement("div");
        section.className = "mb-8 bg-gray-800 rounded-xl border border-gray-700 overflow-hidden shadow-lg";

        if (!esUnicoGrupo) {
            const header = document.createElement("div");
            header.className = "bg-gray-900/50 p-4 border-b border-gray-700";
            header.innerHTML = `<h3 class="text-lg font-bold text-blue-400 flex items-center gap-2"><i data-lucide="layers" class="w-4 h-4"></i> ${nombre}</h3>`;
            section.appendChild(header);
        }

        const tableResponsive = document.createElement("div");
        tableResponsive.className = "overflow-x-auto";
        
        const table = document.createElement("table");
        table.className = "w-full text-left text-sm";
        table.innerHTML = `
            <thead class="bg-gray-900 text-gray-400 uppercase text-xs font-semibold">
                <tr>
                    <th class="p-3 text-center w-12">#</th>
                    <th class="p-3">Equipo</th>
                    <th class="p-3 text-center w-12">PJ</th>
                    <th class="p-3 text-center w-12 text-green-400">G</th>
                    <th class="p-3 text-center w-12 text-gray-400">E</th>
                    <th class="p-3 text-center w-12 text-red-400">P</th>
                    <th class="p-3 text-center w-12 hidden md:table-cell">GF</th>
                    <th class="p-3 text-center w-12 hidden md:table-cell">GC</th>
                    <th class="p-3 text-center w-12 font-bold">DG</th>
                    <th class="p-3 text-center w-16 bg-gray-900/80 text-white font-bold border-l border-gray-700">PTS</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-700 text-gray-300">
                ${renderizarFilas(equipos)}
            </tbody>
        `;

        tableResponsive.appendChild(table);
        section.appendChild(tableResponsive);
        contenedor.appendChild(section);
    }
    
    if(window.lucide) lucide.createIcons();
}

function renderizarFilas(listaEquipos) {
    return listaEquipos.map((item, index) => {
        const posicion = index + 1;
        
        let posClass = "text-gray-500 font-medium";
        let bgClass = index % 2 === 0 ? 'bg-gray-800/30' : 'bg-transparent';
        
        if (posicion === 1) { 
            posClass = "text-yellow-400 font-bold"; 
            bgClass = "bg-yellow-500/10"; 
        } else if (posicion <= 4) { 
            posClass = "text-blue-400 font-bold"; 
        } else if (listaEquipos.length > 5 && posicion >= listaEquipos.length - 1) {
             posClass = "text-red-400 font-bold";
        }

        return `
            <tr class="hover:bg-gray-700/50 transition-colors ${bgClass}">
                <td class="p-3 text-center ${posClass}">${posicion}</td>
                <td class="p-3 font-medium text-white">
                    <div class="flex items-center gap-2">
                         ${item.nombre}
                    </div>
                </td>
                <td class="p-3 text-center text-gray-300">${item.pj}</td>
                <td class="p-3 text-center text-green-400 font-medium">${item.pg}</td>
                <td class="p-3 text-center text-gray-400">${item.pe}</td>
                <td class="p-3 text-center text-red-400">${item.pp}</td>
                <td class="p-3 text-center hidden md:table-cell">${item.gf}</td>
                <td class="p-3 text-center hidden md:table-cell text-gray-500">${item.gc}</td>
                <td class="p-3 text-center font-bold">${item.dg}</td>
                <td class="p-3 text-center font-bold text-white text-base bg-gray-800 border-l border-gray-700">${item.pts}</td>
            </tr>
        `;
    }).join('');
}