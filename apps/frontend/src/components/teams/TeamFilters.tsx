import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { lookupService } from '@/services/lookupService';
import { Search, Filter, X } from 'lucide-react';
import { TeamFilters as FilterState } from '@/services/teamService';

interface TeamFiltersProps {
    filters: FilterState;
    onFilterChange: (filters: FilterState) => void;
}

export default function TeamFilters({ filters, onFilterChange }: TeamFiltersProps) {
    const [search, setSearch] = useState(filters.search || '');

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            if (search !== filters.search) {
                onFilterChange({ ...filters, search });
            }
        }, 500);
        return () => clearTimeout(timer);
    }, [search, filters, onFilterChange]);

    // Data Queries
    const { data: confederations } = useQuery({
        queryKey: ['confederations'],
        queryFn: lookupService.getConfederations
    });

    const { data: countries } = useQuery({
        queryKey: ['countries'],
        queryFn: lookupService.getCountries
    });

    const { data: competitions } = useQuery({
        queryKey: ['competitions', filters.confederacion_id, filters.pais_id],
        queryFn: () => lookupService.getCompetitions(filters.confederacion_id, filters.pais_id),
        enabled: true
    });

    // Helper to clear specific filter
    const handleClear = (key: keyof FilterState) => {
        const newFilters = { ...filters };
        delete newFilters[key];

        // Logic: Clearing confederation might need to clear country if country belonged to it?
        // Actually, logic says: filters are independent but affect dropdown options.
        // If I clear confederation, valid countries list expands.
        // Current selected country MIGHT be invalid if we tracked relation strictly, 
        // but backend flattens logic (country OR confederation).

        onFilterChange(newFilters);
    };

    // Filter available countries based on confederation?
    // Not strictly required by backend logic (filter says "show teams in this country"), 
    // but UI should probably prompt user.
    // However, `getCountries` returns ALL countries currently.
    // Optimization: Filter list locally if confederation selected.
    // We don't have confederation_id in Country interface yet? 
    // Let's assume we do or need to add it, OTW we disable filtering of countries.
    // Backend `Pais` model has `confederacion_id`.
    // Let's verify interface `Country` in lookupService.

    // ... Checked lookupService, Country has only `pais_id`, `nombre`, `iso_code`.
    // So we can't filter countries by confederation locally unless we update interface.
    // For now, show all countries.

    return (
        <div className="bg-si-900 border border-si-800 rounded-lg p-4 mb-6 space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
                {/* Search */}
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-2.5 text-gray-500 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Buscar por nombre..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-si-950 border border-si-800 rounded-md focus:outline-none focus:border-si-accent text-white placeholder-gray-600"
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Confederacion */}
                <div className="space-y-1">
                    <label className="text-xs text-gray-400 font-medium uppercase tracking-wider">Confederación</label>
                    <select
                        value={filters.confederacion_id || ''}
                        onChange={(e) => onFilterChange({ ...filters, confederacion_id: Number(e.target.value) || undefined, competencia_id: undefined })}
                        className="w-full p-2 bg-si-950 border border-si-800 rounded-md text-white focus:outline-none focus:border-si-accent"
                    >
                        <option value="">Todas</option>
                        {confederations?.map(c => (
                            <option key={c.confederacion_id} value={c.confederacion_id}>{c.acronimo || c.nombre}</option>
                        ))}
                    </select>
                </div>

                {/* Pais */}
                <div className="space-y-1">
                    <label className="text-xs text-gray-400 font-medium uppercase tracking-wider">País</label>
                    <select
                        value={filters.pais_id || ''}
                        onChange={(e) => onFilterChange({ ...filters, pais_id: Number(e.target.value) || undefined, competencia_id: undefined })}
                        className="w-full p-2 bg-si-950 border border-si-800 rounded-md text-white focus:outline-none focus:border-si-accent"
                    >
                        <option value="">Todos</option>
                        {countries?.map(c => (
                            <option key={c.pais_id} value={c.pais_id}>{c.nombre}</option>
                        ))}
                    </select>
                </div>

                {/* Competencia */}
                <div className="space-y-1">
                    <label className="text-xs text-gray-400 font-medium uppercase tracking-wider">Competencia</label>
                    <select
                        value={filters.competencia_id || ''}
                        onChange={(e) => onFilterChange({ ...filters, competencia_id: Number(e.target.value) || undefined })}
                        className="w-full p-2 bg-si-950 border border-si-800 rounded-md text-white focus:outline-none focus:border-si-accent"
                        disabled={!filters.confederacion_id && !filters.pais_id && competitions?.length === 0}
                    >
                        <option value="">Todas</option>
                        {competitions?.map(c => (
                            <option key={c.competencia_id} value={c.competencia_id}>{c.nombre}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Active Filters Tags (Optional polish) */}
            {(filters.confederacion_id || filters.pais_id || filters.competencia_id) && (
                <div className="flex gap-2 flex-wrap pt-2 border-t border-si-800/50">
                    {filters.confederacion_id && (
                        <span className="text-xs bg-si-800 text-si-100 px-2 py-1 rounded flex items-center gap-1">
                            Confed: {confederations?.find(c => c.confederacion_id === filters.confederacion_id)?.acronimo}
                            <button onClick={() => handleClear('confederacion_id')} className="hover:text-white"><X size={12} /></button>
                        </span>
                    )}
                    {filters.pais_id && (
                        <span className="text-xs bg-si-800 text-si-100 px-2 py-1 rounded flex items-center gap-1">
                            País: {countries?.find(c => c.pais_id === filters.pais_id)?.nombre}
                            <button onClick={() => handleClear('pais_id')} className="hover:text-white"><X size={12} /></button>
                        </span>
                    )}
                </div>
            )}
        </div>
    );
}
