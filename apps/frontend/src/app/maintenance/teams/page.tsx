'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { teamService, TeamFilters as FilterState } from '@/services/teamService';
import { lookupService } from '@/services/lookupService';
import Link from 'next/link';
import {
    Trash, Edit, Search, Plus, MapPin,
    Trophy, Shield, LayoutGrid, List,
    ArrowUpDown, Filter, X, MoreHorizontal
} from 'lucide-react';
import { PaisSummary, CiudadSummary } from '@/types';

export default function TeamMaintenancePage() {
    // State for Filters
    const [filters, setFilters] = useState<FilterState>({
        search: '',
        pais_id: undefined,
        ciudad_id: undefined,
        elo_min: undefined,
        elo_max: undefined,
        estado: '',
    });

    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [sortBy, setSortBy] = useState<string>('equipo_id');
    const [sortDesc, setSortDesc] = useState<boolean>(true);

    // Lookups
    const { data: countries } = useQuery({ queryKey: ['countries'], queryFn: lookupService.getCountries });
    const { data: cities } = useQuery({
        queryKey: ['cities', filters.pais_id],
        queryFn: () => filters.pais_id ? lookupService.getCities(filters.pais_id) : Promise.resolve([]),
        enabled: !!filters.pais_id
    });

    // Fetch Teams
    const { data: teams, isLoading, isError, refetch } = useQuery({
        queryKey: ['teams', filters, sortBy, sortDesc],
        queryFn: () => teamService.getAll(0, 1000, {
            ...filters,
            sort_by: sortBy,
            sort_desc: sortDesc
        })
    });

    const handleSort = (column: string) => {
        if (sortBy === column) {
            setSortDesc(!sortDesc);
        } else {
            setSortBy(column);
            setSortDesc(false);
        }
    };

    const getEloColor = (elo: number) => {
        if (elo >= 1500) return 'text-yellow-400 border-yellow-400/50 bg-yellow-400/10';
        if (elo >= 1200) return 'text-gray-300 border-gray-400/50 bg-gray-400/10';
        return 'text-orange-400 border-orange-400/50 bg-orange-400/10';
    };

    const StatusBadge = ({ estado }: { estado?: string }) => {
        const colors: Record<string, string> = {
            'ACTIVO': 'bg-si-success/20 text-si-success border-si-success/30',
            'INACTIVO': 'bg-si-danger/20 text-si-danger border-si-danger/30',
            'DESAPARECIDO': 'bg-gray-800 text-gray-400 border-gray-700',
        };
        const colorClass = colors[estado || 'ACTIVO'] || colors['ACTIVO'];
        return (
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${colorClass} tracking-wider`}>
                {estado || 'ACTIVO'}
            </span>
        );
    };

    if (isLoading) return (
        <div className="flex items-center justify-center min-h-[400px]">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-si-accent"></div>
        </div>
    );

    return (
        <div className="space-y-6 pb-20">
            {/* Header & Main Actions */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight uppercase italic flex items-center gap-3">
                        <Shield className="w-8 h-8 text-si-accent" />
                        Team Management
                    </h1>
                    <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-medium">
                        Database Maintenance / {teams?.length || 0} Records
                    </p>
                </div>
                <Link
                    href="/maintenance/teams/create"
                    className="bg-si-accent hover:bg-blue-600 text-white px-6 py-2.5 rounded-lg font-bold shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 group"
                >
                    <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
                    CREATE NEW TEAM
                </Link>
            </div>

            {/* Toolbar: Search, Sort & Filter Activation */}
            <div className="bg-si-800/40 backdrop-blur-sm border border-si-800 p-2 rounded-xl flex flex-col lg:flex-row gap-2">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search teams by name or TLA..."
                        className="w-full bg-si-900/50 border-none pl-11 pr-4 py-3 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-si-accent"
                        value={filters.search || ''}
                        onChange={e => setFilters({ ...filters, search: e.target.value })}
                    />
                </div>

                <div className="flex items-center gap-2">
                    <select
                        className="bg-si-900/50 border-none text-gray-300 py-3 pl-4 pr-10 rounded-lg text-sm focus:ring-2 focus:ring-si-accent"
                        value={`${sortBy}|${sortDesc}`}
                        onChange={(e) => {
                            const [field, desc] = e.target.value.split('|');
                            setSortBy(field);
                            setSortDesc(desc === 'true');
                        }}
                    >
                        <option value="equipo_id|false">Oldest First</option>
                        <option value="equipo_id|true">Newest First</option>
                        <option value="nombre|false">Name A-Z</option>
                        <option value="nombre|true">Name Z-A</option>
                        <option value="elo|true">Highest ELO</option>
                        <option value="elo|false">Lowest ELO</option>
                    </select>

                    <button
                        onClick={() => setIsFilterOpen(!isFilterOpen)}
                        className={`p-3 rounded-lg border transition-colors flex items-center gap-2 text-sm font-bold ${isFilterOpen ? 'bg-si-accent border-si-accent text-white' : 'bg-si-900/50 border-si-800 text-gray-400 hover:text-white'}`}
                    >
                        <Filter className="w-5 h-5" />
                        {isFilterOpen ? 'HIDE FILTERS' : 'FILTERS'}
                    </button>
                </div>
            </div>

            {/* Collapsible Filters */}
            {isFilterOpen && (
                <div className="bg-si-900/80 border border-si-800 p-6 rounded-xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in slide-in-from-top-2 duration-300">
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Country</label>
                        <select
                            className="w-full bg-si-800 border-si-700 text-white p-2.5 rounded-lg focus:ring-si-accent"
                            value={filters.pais_id || ''}
                            onChange={e => setFilters({ ...filters, pais_id: e.target.value ? Number(e.target.value) : undefined, ciudad_id: undefined })}
                        >
                            <option value="">All Countries</option>
                            {countries?.map((c: PaisSummary) => (
                                <option key={c.pais_id} value={c.pais_id}>{c.nombre}</option>
                            ))}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">City</label>
                        <select
                            className="w-full bg-si-800 border-si-700 text-white p-2.5 rounded-lg focus:ring-si-accent disabled:opacity-50"
                            value={filters.ciudad_id || ''}
                            disabled={!filters.pais_id}
                            onChange={e => setFilters({ ...filters, ciudad_id: e.target.value ? Number(e.target.value) : undefined })}
                        >
                            <option value="">All Cities</option>
                            {cities?.map((c: CiudadSummary) => (
                                <option key={c.ciudad_id} value={c.ciudad_id}>{c.nombre}</option>
                            ))}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">ELO Range</label>
                        <div className="flex items-center gap-2">
                            <input
                                type="number" placeholder="Min"
                                className="w-full bg-si-800 border-si-700 text-white p-2 rounded-lg text-sm"
                                value={filters.elo_min || ''}
                                onChange={e => setFilters({ ...filters, elo_min: e.target.value ? Number(e.target.value) : undefined })}
                            />
                            <span className="text-gray-600">-</span>
                            <input
                                type="number" placeholder="Max"
                                className="w-full bg-si-800 border-si-700 text-white p-2 rounded-lg text-sm"
                                value={filters.elo_max || ''}
                                onChange={e => setFilters({ ...filters, elo_max: e.target.value ? Number(e.target.value) : undefined })}
                            />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Status</label>
                        <select
                            className="w-full bg-si-800 border-si-700 text-white p-2.5 rounded-lg focus:ring-si-accent"
                            value={filters.estado || ''}
                            onChange={e => setFilters({ ...filters, estado: e.target.value })}
                        >
                            <option value="">All</option>
                            <option value="ACTIVO">Activo</option>
                            <option value="INACTIVO">Inactivo</option>
                            <option value="DESAPARECIDO">Desaparecido</option>
                        </select>
                    </div>
                </div>
            )}

            {/* Team Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {teams?.map((team) => (
                    <div key={team.equipo_id} className="bg-si-800/30 border border-si-800 rounded-2xl overflow-hidden hover:border-si-accent/50 transition-all group hover:translate-y-[-4px] hover:shadow-2xl hover:shadow-black">
                        {/* Card Top: Crest & ELO */}
                        <div className="p-5 flex justify-between items-start">
                            <div className="flex gap-4">
                                <div className="w-16 h-16 bg-si-900 rounded-xl border border-si-700 flex items-center justify-center p-2 relative overflow-hidden group-hover:border-si-accent transition-colors">
                                    {team.escudo_url ? (
                                        <img
                                            src={`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}${team.escudo_url}`}
                                            alt={team.nombre}
                                            className="w-full h-full object-contain"
                                        />
                                    ) : (
                                        <Shield className="w-8 h-8 text-gray-600" />
                                    )}
                                    <div className="absolute inset-0 bg-si-accent/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                                <div>
                                    <h3 className="text-white font-bold leading-tight group-hover:text-si-accent transition-colors">
                                        {team.nombre}
                                    </h3>
                                    <div className="flex items-center gap-2 mt-1">
                                        <span className="bg-si-accent/20 text-si-accent px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-tighter">
                                            {team.codigo_tla || 'TLA'}
                                        </span>
                                        <StatusBadge estado={team.estado} />
                                    </div>
                                </div>
                            </div>

                            <div className={`flex flex-col items-center border rounded-lg px-2 py-1 min-w-[50px] ${getEloColor(team.rating?.elo_actual || team.elo || 1000)}`}>
                                <span className="text-[10px] font-bold uppercase opacity-60">ELO</span>
                                <span className="text-lg font-black leading-none">{team.rating?.elo_actual ?? team.elo ?? '---'}</span>
                            </div>
                        </div>

                        {/* Card Center: Info */}
                        <div className="px-5 pb-4 space-y-2">
                            <div className="flex items-center gap-2 text-xs text-gray-400">
                                <MapPin className="w-3.5 h-3.5 text-si-accent" />
                                <span className="truncate">{team.ciudad_sede?.nombre}, {team.pais?.nombre}</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-gray-400">
                                <Trophy className="w-3.5 h-3.5 text-si-accent" />
                                <span>Founded in {team.anio_fundacion || '---'}</span>
                            </div>
                        </div>

                        {/* Card Bottom: Actions */}
                        <div className="bg-si-900/50 p-4 border-t border-si-800 flex items-center justify-between">
                            <div className="flex gap-2">
                                <Link
                                    href={`/maintenance/teams/${team.equipo_id}`}
                                    className="bg-si-800 hover:bg-si-700 text-gray-300 p-2 rounded-lg transition-colors border border-si-700"
                                    title="Edit Team"
                                >
                                    <Edit className="w-4 h-4" />
                                </Link>
                                <button
                                    onClick={() => {
                                        if (confirm(`Delete ${team.nombre}?`)) {
                                            teamService.delete(team.equipo_id).then(() => refetch());
                                        }
                                    }}
                                    className="bg-si-danger/10 hover:bg-si-danger/20 text-si-danger p-2 rounded-lg transition-colors border border-si-danger/30"
                                    title="Delete Team"
                                >
                                    <Trash className="w-4 h-4" />
                                </button>
                            </div>
                            <Link
                                href={`/maintenance/teams/${team.equipo_id}`}
                                className="text-[10px] font-black italic tracking-widest text-si-accent hover:text-white transition-colors"
                            >
                                MANAGE VIEW
                            </Link>
                        </div>
                    </div>
                ))}
            </div>

            {/* Empty State */}
            {teams?.length === 0 && (
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <Shield className="w-20 h-20 text-si-800 mb-4" />
                    <h2 className="text-xl font-bold text-gray-400">No teams found</h2>
                    <p className="text-gray-600 mt-2">Try adjusting your filters or create a new team.</p>
                </div>
            )}

            <div className="flex justify-between items-center bg-si-800/40 p-4 rounded-xl border border-si-800 text-sm">
                <p className="text-gray-500 font-medium">
                    Showing <span className="text-si-accent font-bold">{teams?.length || 0}</span> team records
                </p>
                <div className="flex gap-4 text-[10px] font-black text-gray-600 uppercase tracking-widest">
                    <span>Alpha 1.0</span>
                    <span className="text-si-accent">Simfut Engine</span>
                </div>
            </div>
        </div>
    );
}
