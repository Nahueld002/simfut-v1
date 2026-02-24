import { useState } from 'react';
import { Rivalidad } from '@/types';
import { lookupService } from '@/services/lookupService';
import { useQuery } from '@tanstack/react-query';
import { Trash, Plus } from 'lucide-react';

interface RivalryManagerProps {
    equipoId: number | null;
    rivalries: Rivalidad[];
    onAdd: (rivalry: Partial<Rivalidad>) => void;
    onDelete: (id: number | string) => void;
}

export default function RivalryManager({ equipoId, rivalries = [], onAdd, onDelete }: RivalryManagerProps) {
    const [isAdding, setIsAdding] = useState(false);
    const [selectedTeamId, setSelectedTeamId] = useState<number | ''>('');
    const [intensity, setIntensity] = useState(50);
    const [name, setName] = useState('');

    // Fetch all teams for dropdown
    const { data: allTeams } = useQuery({
        queryKey: ['teams_lookup'],
        queryFn: lookupService.getTeams
    });

    const handleAdd = () => {
        if (!selectedTeamId) return;
        onAdd({
            equipo_a_id: equipoId || 0, // Parent will handle if equipoId is null (new team)
            equipo_b_id: Number(selectedTeamId),
            nombre: name || undefined,
            intensidad: intensity
        });
        setIsAdding(false);
        setSelectedTeamId('');
        setIntensity(50);
        setName('');
    };

    // Filter out current team and existing rivals from dropdown
    const availableTeams = allTeams?.filter(t =>
        t.equipo_id !== equipoId &&
        !rivalries?.some(r => r.equipo_a_id === t.equipo_id || r.equipo_b_id === t.equipo_id)
    ) || [];

    return (
        <div className="bg-gray-800 p-6 rounded-lg shadow-md border border-gray-700">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-100">Rivalries</h3>
                <button
                    type="button"
                    onClick={() => setIsAdding(!isAdding)}
                    className="flex items-center gap-1 text-sm text-green-400 hover:text-green-300 font-medium"
                >
                    <Plus className="w-4 h-4" /> Add Rivalry
                </button>
            </div>

            {isAdding && (
                <div className="bg-gray-700/50 p-4 rounded-md mb-4 border border-gray-600">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">Opponent</label>
                            <select
                                value={selectedTeamId}
                                onChange={(e) => setSelectedTeamId(Number(e.target.value))}
                                className="w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:border-green-500 focus:ring-green-500"
                            >
                                <option value="">Select Team</option>
                                {availableTeams.map(t => {
                                    const location = [
                                        t.ciudad_sede?.nombre,
                                        t.pais?.nombre
                                    ].filter(Boolean).join(', ');

                                    return (
                                        <option key={t.equipo_id} value={t.equipo_id}>
                                            {t.nombre} {location ? `(${location})` : ''}
                                        </option>
                                    );
                                })}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1">Intensity (0-100)</label>
                            <input
                                type="number"
                                min="0" max="100"
                                value={intensity}
                                onChange={(e) => setIntensity(Number(e.target.value))}
                                className="w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:border-green-500 focus:ring-green-500"
                            />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-300 mb-1">Name (Optional)</label>
                            <input
                                type="text"
                                placeholder="e.g. El Clásico"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:border-green-500 focus:ring-green-500"
                            />
                        </div>
                    </div>
                    <div className="mt-3 flex justify-end gap-2">
                        <button type="button" onClick={() => setIsAdding(false)} className="px-3 py-1 text-sm text-gray-400 hover:text-gray-200">Cancel</button>
                        <button
                            type="button"
                            onClick={handleAdd}
                            disabled={!selectedTeamId}
                            className="px-3 py-1 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 disabled:opacity-50"
                        >
                            Add to Draft
                        </button>
                    </div>
                </div>
            )}

            <div className="space-y-3">
                {rivalries?.length === 0 ? (
                    <p className="text-sm text-gray-500 italic">No rivalries in this draft.</p>
                ) : (
                    rivalries?.map(r => {
                        // Find the OTHER team name
                        const otherId = r.equipo_a_id === equipoId ? r.equipo_b_id : r.equipo_a_id;
                        const otherTeam = allTeams?.find(t => t.equipo_id === otherId);

                        // Local key might be rivalidad_id (if existing) or a temp one
                        const key = r.rivalidad_id || `temp-${r.equipo_b_id}`;

                        return (
                            <div key={key} className="flex justify-between items-center p-3 bg-gray-700/30 rounded-md border border-gray-600">
                                <div>
                                    <span className="font-medium text-gray-100">{otherTeam?.nombre || `Team ${otherId}`}</span>
                                    {r.nombre && <span className="ml-2 text-xs text-blue-300 bg-blue-900/40 px-2 py-0.5 rounded-full border border-blue-800">{r.nombre}</span>}
                                    <div className="text-xs text-gray-400 mt-0.5">Intensity: {r.intensidad}/100</div>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => onDelete(key)}
                                    className="text-red-400 hover:text-red-300 p-1 rounded-full hover:bg-red-900/20"
                                    title="Remove Rivalry"
                                >
                                    <Trash className="w-4 h-4" />
                                </button>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
