'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { competitionService, Competencia } from '@/services/competitionService';
import { lookupService } from '@/services/lookupService';
import Link from 'next/link';
import {
    Search, Plus, Trophy,
    Filter, X, MapPin, Globe, Shield
} from 'lucide-react';

export default function CompetitionsPage() {
    const [search, setSearch] = useState('');
    const [mundoId, setMundoId] = useState<number | undefined>(1); // Default world 1

    const { data: competitions, isLoading } = useQuery({
        queryKey: ['competitions', mundoId],
        queryFn: () => competitionService.getAll(0, 100, mundoId)
    });

    const filteredCompetitions = competitions?.filter(c =>
        c.nombre.toLowerCase().includes(search.toLowerCase())
    );

    if (isLoading) return (
        <div className="flex items-center justify-center min-h-[400px]">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-si-accent"></div>
        </div>
    );

    return (
        <div className="space-y-6 pb-20">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight uppercase italic flex items-center gap-3">
                        <Trophy className="w-8 h-8 text-si-accent" />
                        Competitions
                    </h1>
                    <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-medium">
                        Management Portal / {filteredCompetitions?.length || 0} Templates
                    </p>
                </div>
                <Link
                    href="/maintenance/competitions/create"
                    className="bg-si-accent hover:bg-blue-600 text-white px-6 py-2.5 rounded-lg font-bold shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 group"
                >
                    <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
                    CREATE COMPETITION
                </Link>
            </div>

            <div className="bg-si-800/40 backdrop-blur-sm border border-si-800 p-2 rounded-xl flex flex-col lg:flex-row gap-2">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search competitions by name..."
                        className="w-full bg-si-900/50 border-none pl-11 pr-4 py-3 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-si-accent"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {filteredCompetitions?.map((comp) => (
                    <div key={comp.competencia_id} className="bg-si-800/30 border border-si-800 rounded-2xl overflow-hidden hover:border-si-accent/50 transition-all group hover:translate-y-[-4px]">
                        <div className="p-5 flex justify-between items-start">
                            <div className="flex gap-4">
                                <div className="w-16 h-16 bg-si-900 rounded-xl border border-si-700 flex items-center justify-center p-2 relative overflow-hidden group-hover:border-si-accent transition-colors">
                                    <Trophy className="w-8 h-8 text-gray-600" />
                                </div>
                                <div>
                                    <h3 className="text-white font-bold leading-tight group-hover:text-si-accent transition-colors">
                                        {comp.nombre}
                                    </h3>
                                    <div className="flex items-center gap-2 mt-1">
                                        <span className="bg-si-accent/20 text-si-accent px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-tighter">
                                            {comp.reputacion_base} REP
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="px-5 pb-4 space-y-2">
                            <div className="flex items-center gap-2 text-xs text-gray-400">
                                <Globe className="w-3.5 h-3.5 text-si-accent" />
                                <span>{comp.confederacion_id ? 'International' : comp.pais_id ? 'National' : 'Other'}</span>
                            </div>
                        </div>

                        <div className="bg-si-900/50 p-4 border-t border-si-800 flex items-center justify-between">
                            <Link
                                href={`/maintenance/competitions/${comp.competencia_id}`}
                                className="bg-si-800 hover:bg-si-700 text-gray-300 px-4 py-2 rounded-lg transition-colors border border-si-700 text-xs font-bold"
                            >
                                CONFIGURE
                            </Link>
                            <Link
                                href={`/maintenance/competitions/${comp.competencia_id}`}
                                className="text-[10px] font-black italic tracking-widest text-si-accent hover:text-white transition-colors"
                            >
                                VIEW DETAILS
                            </Link>
                        </div>
                    </div>
                ))}
            </div>

            {filteredCompetitions?.length === 0 && (
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <Trophy className="w-20 h-20 text-si-800 mb-4" />
                    <h2 className="text-xl font-bold text-gray-400">No competitions found</h2>
                </div>
            )}
        </div>
    );
}
