'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { competitionService, CompetenciaEdicion, Etapa, Participante } from '@/services/competitionService';
import { lookupService } from '@/services/lookupService';
import Link from 'next/link';
import {
    Save, ArrowLeft, Settings,
    ListTree, Users, Calendar, BarChart3,
    Plus, Trash, Zap
} from 'lucide-react';

export default function EditionDetailPage() {
    const params = useParams();
    const router = useRouter();
    const queryClient = useQueryClient();
    const id = Number(params?.id);
    const [activeTab, setActiveTab] = useState<'general' | 'structure' | 'participants' | 'fixture' | 'table'>('general');

    const [formData, setFormData] = useState<Partial<CompetenciaEdicion>>({});
    const [draftStages, setDraftStages] = useState<Partial<Etapa>[]>([]);
    const [draftParticipants, setDraftParticipants] = useState<any[]>([]);

    const { data: edition, isLoading } = useQuery({
        queryKey: ['edition', id],
        queryFn: () => competitionService.getEditionById(id)
    });

    const { data: etapaTipos } = useQuery({ queryKey: ['etapa_tipos'], queryFn: () => lookupService.getByDomain('ETAPA_TIPO') });
    const { data: teams } = useQuery({ queryKey: ['all_teams'], queryFn: lookupService.getTeams });
    const { data: initialStages } = useQuery({ queryKey: ['initial-stages', id], queryFn: () => competitionService.getStages(id), enabled: !!id });
    const { data: initialParticipants } = useQuery({ queryKey: ['initial-participants', id], queryFn: () => competitionService.getParticipants(id), enabled: !!id });
    const { data: clasifMetodos } = useQuery({ queryKey: ['clasif_metodos'], queryFn: () => lookupService.getByDomain('METODO_CLASIFICACION') });

    const [teamSearch, setTeamSearch] = useState('');

    useEffect(() => {
        if (edition) setFormData(edition);
    }, [edition]);

    useEffect(() => {
        if (initialStages) setDraftStages(initialStages);
    }, [initialStages]);

    useEffect(() => {
        if (initialParticipants) setDraftParticipants(initialParticipants);
    }, [initialParticipants]);

    const saveMutation = useMutation({
        mutationFn: async () => {
            await competitionService.updateEdition(id, formData);
            await competitionService.syncStages(id, draftStages);
            await competitionService.syncParticipants(id, draftParticipants);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['edition', id] });
            alert('Edition updated successfully!');
        }
    });

    const generateFixtureMutation = useMutation({
        mutationFn: () => competitionService.generateFixture(id),
        onSuccess: (res) => {
            alert(res.message);
            setActiveTab('fixture');
        },
        onError: (err) => alert('Error generating fixture: ' + err)
    });

    if (isLoading) return <div className="p-20 text-center text-si-accent animate-pulse font-black">LOADING EDITION...</div>;

    const tabs = [
        { id: 'general', label: 'General', icon: Settings },
        { id: 'structure', label: 'Structure', icon: ListTree },
        { id: 'participants', label: 'Participants', icon: Users },
        { id: 'fixture', label: 'Fixture', icon: Calendar },
        { id: 'table', label: 'Table', icon: BarChart3 },
    ];

    return (
        <div className="pb-20 min-h-screen bg-si-900 text-gray-100">
            {/* Header */}
            <div className="sticky top-0 z-30 bg-si-900/80 backdrop-blur-md border-b border-si-800 px-8 py-4 mb-8">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center gap-4">
                        <button onClick={() => router.back()} className="p-2 hover:bg-si-800 rounded-lg transition-colors text-gray-400">
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <div>
                            <h1 className="text-xl font-black tracking-tight uppercase italic text-white">
                                {edition?.nombre_display || `Edition ${id}`}
                            </h1>
                            <p className="text-[10px] font-bold text-si-accent uppercase tracking-widest">
                                Competition Instance Management
                            </p>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={() => generateFixtureMutation.mutate()}
                            className="bg-si-800 hover:bg-si-700 text-si-accent px-6 py-2.5 rounded-lg font-black transition-all flex items-center gap-2 border border-si-accent/30"
                        >
                            <Zap className="w-5 h-5" />
                            GENERATE FIXTURE
                        </button>
                        <button
                            onClick={() => saveMutation.mutate()}
                            className="bg-si-accent hover:bg-blue-600 text-white px-8 py-2.5 rounded-lg font-black shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2"
                        >
                            <Save className="w-5 h-5" />
                            SAVE CHANGES
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-8">
                {/* Tabs */}
                <div className="flex flex-wrap gap-2 mb-8 bg-si-800/30 p-1.5 rounded-xl border border-si-800 w-fit">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        const isActive = activeTab === tab.id;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-xs font-black transition-all tracking-widest uppercase italic ${isActive
                                    ? 'bg-si-accent text-white'
                                    : 'text-gray-500 hover:text-gray-300 hover:bg-si-800/50'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        );
                    })}
                </div>

                {/* Content */}
                <div className="animate-in fade-in duration-500">
                    {activeTab === 'general' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 space-y-6">
                            <div>
                                <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">Display Name</label>
                                <input
                                    type="text"
                                    className="w-full bg-si-900 border-si-700 text-white rounded-xl p-4 text-xl font-bold italic"
                                    value={formData.nombre_display || ''}
                                    onChange={e => setFormData({ ...formData, nombre_display: e.target.value })}
                                />
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">Start Date</label>
                                    <input type="date" className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3" value={String(formData.fecha_inicio || '')} onChange={e => setFormData({ ...formData, fecha_inicio: e.target.value })} />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">End Date</label>
                                    <input type="date" className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3" value={String(formData.fecha_fin || '')} onChange={e => setFormData({ ...formData, fecha_fin: e.target.value })} />
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'structure' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 space-y-8">
                            <div className="flex justify-between items-center">
                                <h2 className="text-xl font-black italic uppercase">Competition Structure</h2>
                                <button
                                    onClick={() => setDraftStages([...draftStages, { edicion_id: id, orden: draftStages.length + 1, nombre: 'New Stage', tipo_id: 11 }])}
                                    className="text-si-accent flex items-center gap-2 font-bold text-xs uppercase tracking-widest"
                                >
                                    <Plus className="w-4 h-4" /> ADD STAGE
                                </button>
                            </div>

                            <div className="space-y-4">
                                {draftStages.map((s, idx) => (
                                    <div key={idx} className="p-6 bg-si-900/50 rounded-2xl border border-si-700 flex flex-col md:flex-row gap-6 items-center">
                                        <div className="w-10 h-10 bg-si-accent text-white rounded-lg flex items-center justify-center font-black">
                                            {s.orden}
                                        </div>
                                        <div className="flex-1">
                                            <input
                                                className="bg-transparent border-none text-white font-bold p-0 w-full focus:ring-0"
                                                value={s.nombre}
                                                onChange={e => {
                                                    const copy = [...draftStages];
                                                    copy[idx].nombre = e.target.value;
                                                    setDraftStages(copy);
                                                }}
                                            />
                                            <select
                                                className="bg-transparent border-none text-[10px] text-si-accent font-black uppercase tracking-tighter p-0 mt-1 focus:ring-0"
                                                value={s.tipo_id}
                                                onChange={e => {
                                                    const copy = [...draftStages];
                                                    copy[idx].tipo_id = Number(e.target.value);
                                                    setDraftStages(copy);
                                                }}
                                            >
                                                {etapaTipos?.map(t => <option key={t.id} value={t.id} className="bg-si-900">{t.codigo.replace('_', ' ')}</option>)}
                                            </select>
                                        </div>
                                        <button onClick={() => setDraftStages(draftStages.filter((_, i) => i !== idx))} className="text-si-danger hover:bg-si-danger/10 p-2 rounded-lg transition-colors">
                                            <Trash className="w-5 h-5" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {activeTab === 'participants' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 space-y-8">
                            <div className="space-y-4">
                                <div className="bg-si-900/50 p-4 rounded-xl border border-si-700">
                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">Add Team</label>
                                    <div className="flex gap-2">
                                        <select
                                            className="flex-1 bg-si-800 border-none text-white text-sm rounded-lg p-2 focus:ring-1 focus:ring-si-accent"
                                            onChange={(e) => {
                                                const teamId = Number(e.target.value);
                                                if (teamId) {
                                                    const teamObj = teams?.find(t => t.equipo_id === teamId);
                                                    if (teamObj && !draftParticipants.some(p => p.equipo_id === teamId)) {
                                                        setDraftParticipants([...draftParticipants, { edicion_id: id, equipo_id: teamId, equipo_nombre: teamObj.nombre }]);
                                                    }
                                                    e.target.value = "";
                                                }
                                            }}
                                        >
                                            <option value="">Search team...</option>
                                            {teams?.filter(t => !draftParticipants.some(p => p.equipo_id === t.equipo_id)).slice(0, 100).map(t => (
                                                <option key={t.equipo_id} value={t.equipo_id}>{t.nombre}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {draftParticipants.map((p, idx) => (
                                        <div key={idx} className="p-4 bg-si-900/50 rounded-xl border border-si-700 flex justify-between items-center group hover:border-si-accent/50 transition-all">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 bg-si-800 rounded flex items-center justify-center text-[10px] font-black text-si-accent">#{p.equipo_id}</div>
                                                <span className="font-bold text-sm text-gray-200">{p.equipo_nombre || `Team ${p.equipo_id}`}</span>
                                            </div>
                                            <button onClick={() => setDraftParticipants(draftParticipants.filter((_, i) => i !== idx))} className="text-gray-600 hover:text-si-danger transition-colors">
                                                <Trash className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ))}
                                    {draftParticipants.length === 0 && (
                                        <div className="col-span-full py-10 text-center text-gray-500 italic border-2 border-dashed border-si-800 rounded-2xl">
                                            No participants added.
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'fixture' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 text-center">
                            <Calendar className="w-16 h-16 text-si-accent mx-auto mb-4" />
                            <h2 className="text-xl font-black italic uppercase">Fixture & Match Progress</h2>
                            <p className="text-gray-500 mt-2">Generate fixture or view scheduled matches.</p>
                        </div>
                    )}

                    {activeTab === 'table' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 text-center">
                            <BarChart3 className="w-16 h-16 text-si-success mx-auto mb-4" />
                            <h2 className="text-xl font-black italic uppercase">Positions Table</h2>
                            <p className="text-gray-500 mt-2">Live standings based on match results.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
