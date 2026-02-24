import { useState } from 'react';
import { EstadioHist } from '@/types';
import { lookupService } from '@/services/lookupService';
import { useQuery } from '@tanstack/react-query';
import { Plus, Trash } from 'lucide-react';

interface StadiumManagerProps {
    equipoId: number | null;
    countryId?: number;
    history: EstadioHist[];
    onAdd: (record: Partial<EstadioHist>) => void;
    onDelete: (index: number) => void;
}

export default function StadiumManager({ equipoId, countryId, history = [], onAdd, onDelete }: StadiumManagerProps) {
    const [isAdding, setIsAdding] = useState(false);

    // Form state
    const [estadioId, setEstadioId] = useState<number | ''>('');
    const [fechaInicio, setFechaInicio] = useState('');
    const [fechaFin, setFechaFin] = useState('');
    const [motivo, setMotivo] = useState('');
    const [esPrincipal, setEsPrincipal] = useState(true);

    // Fetch stadiums filtered by country
    const { data: allStadiums } = useQuery({
        queryKey: ['stadiums_lookup', countryId],
        queryFn: () => lookupService.getStadiums(countryId),
        enabled: !!countryId || countryId === undefined // Fetch all if no countryId provided, or wait for it
    });

    const handleAdd = () => {
        if (!estadioId || !fechaInicio) return;
        onAdd({
            equipo_id: equipoId || 0,
            estadio_id: Number(estadioId),
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin || undefined,
            motivo: motivo || undefined,
            es_principal: esPrincipal
        });
        setIsAdding(false);
        // Reset form
        setEstadioId('');
        setFechaInicio('');
        setFechaFin('');
        setMotivo('');
        setEsPrincipal(true);
    };

    return (
        <div className="bg-gray-800 p-6 rounded-lg shadow-md border border-gray-700">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-100">Stadium History</h3>
                <button
                    type="button"
                    onClick={() => setIsAdding(!isAdding)}
                    className="flex items-center gap-1 text-sm text-green-400 hover:text-green-300 font-medium"
                >
                    <Plus className="w-4 h-4" /> Add Record
                </button>
            </div>

            {isAdding && (
                <div className="bg-gray-700/50 p-4 rounded-md mb-4 border border-gray-600">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-300 mb-1">Stadium</label>
                            <select
                                value={estadioId}
                                onChange={(e) => setEstadioId(Number(e.target.value))}
                                className="w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:border-green-500 focus:ring-green-500"
                            >
                                <option value="">Select Stadium</option>
                                {allStadiums?.map(s => (
                                    <option key={s.estadio_id} value={s.estadio_id}>{s.nombre}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">Start Date</label>
                            <input
                                type="date"
                                value={fechaInicio}
                                onChange={(e) => setFechaInicio(e.target.value)}
                                className="w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:border-green-500 focus:ring-green-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">End Date (Optional)</label>
                            <input
                                type="date"
                                value={fechaFin}
                                onChange={(e) => setFechaFin(e.target.value)}
                                className="w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:border-green-500 focus:ring-green-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">Reason (Optional)</label>
                            <input
                                type="text"
                                placeholder="e.g. Renovation"
                                value={motivo}
                                onChange={(e) => setMotivo(e.target.value)}
                                className="w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:border-green-500 focus:ring-green-500"
                            />
                        </div>

                        <div className="flex items-end">
                            <label className="flex items-center space-x-2 cursor-pointer pb-2">
                                <input
                                    type="checkbox"
                                    checked={esPrincipal}
                                    onChange={(e) => setEsPrincipal(e.target.checked)}
                                    className="rounded border-gray-600 bg-gray-700 text-green-500 focus:ring-green-500"
                                />
                                <span className="text-sm font-medium text-gray-300">Set as Principal</span>
                            </label>
                        </div>
                    </div>
                    <div className="mt-3 flex justify-end gap-2">
                        <button type="button" onClick={() => setIsAdding(false)} className="px-3 py-1 text-sm text-gray-400 hover:text-gray-200">Cancel</button>
                        <button
                            type="button"
                            onClick={handleAdd}
                            disabled={!estadioId || estadioId === 0 || !fechaInicio}
                            className="px-3 py-1 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Add to Draft
                        </button>
                    </div>
                </div>
            )}

            <div className="space-y-3">
                {history?.length === 0 ? (
                    <p className="text-sm text-gray-500 italic">No historical records in this draft.</p>
                ) : (
                    history?.map((h, i) => {
                        const stadiumName = allStadiums?.find(s => s.estadio_id === h.estadio_id)?.nombre || `Stadium ${h.estadio_id}`;
                        return (
                            <div key={i} className="p-3 bg-gray-700/30 rounded-md border border-gray-600 flex flex-col sm:flex-row justify-between sm:items-center">
                                <div>
                                    <div className="font-medium text-gray-100 flex items-center gap-2">
                                        {stadiumName}
                                        {h.es_principal && <span className="bg-blue-900/40 text-blue-300 text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wide font-bold border border-blue-800">Main</span>}
                                    </div>
                                    <div className="text-xs text-gray-400 mt-1">
                                        {h.fecha_inicio} {h.fecha_fin ? `to ${h.fecha_fin}` : '(Present)'}
                                    </div>
                                </div>
                                <div className="flex items-center gap-3 mt-2 sm:mt-0">
                                    {h.motivo && (
                                        <div className="text-xs text-gray-400 italic bg-gray-800 px-2 py-1 rounded border border-gray-700">
                                            {h.motivo}
                                        </div>
                                    )}
                                    <button
                                        type="button"
                                        onClick={() => onDelete(i)}
                                        className="text-red-400 hover:text-red-300 p-1 rounded-full hover:bg-red-900/20"
                                        title="Remove Record"
                                    >
                                        <Trash className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
