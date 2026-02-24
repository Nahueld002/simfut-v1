'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { teamService } from '@/services/teamService';
import { lookupService } from '@/services/lookupService';
import { EquipoCreateInput, Rivalidad, EstadioHist } from '@/types';
import Link from 'next/link';
import {
    Save, ArrowLeft, Shield, Trophy,
    MoreHorizontal, MapPin, LayoutGrid
} from 'lucide-react';
import RivalryManager from '@/components/teams/RivalryManager';
import StadiumManager from '@/components/teams/StadiumManager';

const StatusBadge = ({ estado }: { estado?: string }) => {
    const colors: Record<string, string> = {
        'ACTIVO': 'bg-si-success/20 text-si-success border-si-success/30',
        'INACTIVO': 'bg-si-danger/20 text-si-danger border-si-danger/30',
        'DESAPARECIDO': 'bg-gray-800 text-gray-400 border-gray-700',
        'CONFIGURED': 'bg-si-accent/20 text-si-accent border-si-accent/30',
        'AUTO': 'bg-si-800 text-gray-500 border-si-700',
    };
    const colorClass = colors[estado || 'ACTIVO'] || colors['ACTIVO'];
    return (
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${colorClass} tracking-wider`}>
            {estado || 'ACTIVO'}
        </span>
    );
};

export default function TeamFormPage() {
    const params = useParams();
    const router = useRouter();
    const queryClient = useQueryClient();
    const rawId = params?.id;
    const isCreating = rawId === 'create';
    const id = (!isCreating && rawId) ? Number(rawId) : null;
    const isEditing = !!id && !isCreating;
    const [activeTab, setActiveTab] = useState<'general' | 'performance' | 'finance' | 'relations'>('general');

    // Form State
    const [formData, setFormData] = useState<Partial<EquipoCreateInput>>({
        nombre: '',
        mundo_id: 1,
        pais_origen_id: 0,
        estado_id: undefined, // Let backend assign default 'ACTIVO' if empty
        colores: { primario: '#000000', secundario: '#ffffff' },
        rating: {
            ataque: 50, defensa: 50, mediocampo: 50, moral: 50, cohesion: 50, fatiga: 0, disciplina: 50,
            estilo_id: undefined, salida_id: undefined, transicion_id: undefined,
            tactica_detalle: {}
        },
        institucion: {
            reputacion_historica: 10,
            hinchada: 10,
            infraestructura: 10,
            estabilidad_directiva: 10,
            nivel_scouting: 10,
            nivel_entrenamiento: 10,
            nivel_juveniles: 10,
            volatilidad: 50,
            potencial_basal: 1200
        },
        finanzas: {
            presupuesto_fichajes: 0,
            presupuesto_salarial: 0,
            poder_economico_base: 10,
            moneda_id: 52, // Default USD (parametro_id)
            paciencia_directiva: 10,
            deuda_total: 0,
            tipo_propiedad_id: undefined
        }
    });

    // --- Draft State for Relations ---
    const [draftRivalries, setDraftRivalries] = useState<Rivalidad[]>([]);
    const [draftStadiumHistory, setDraftStadiumHistory] = useState<(EstadioHist & { isNew?: boolean })[]>([]);
    const [rivalriesToDelete, setRivalriesToDelete] = useState<number[]>([]);
    // Actually the backend endpoint only has CREATE / stadiums/.
    // Let's track new vs existing for stadiums too if we want deletion.

    // Aux State for Cascades
    const [selectedConfed, setSelectedConfed] = useState<number | ''>('');
    const [selectedRegion, setSelectedRegion] = useState<number | ''>('');
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            const { media_id, url } = await teamService.uploadMedia(file, 'escudo');
            setFormData(prev => ({ ...prev, escudo_media_id: media_id }));
            // Construct full URL for preview. Assuming backend is on localhost:8000
            setPreviewUrl(`http://127.0.0.1:8000${url}`);
        } catch (error) {
            console.error('Error uploading image:', error);
            alert('Error uploading image');
        }
    };

    // Fetch Data
    const { data: team, isLoading: isLoadingTeam } = useQuery({
        queryKey: ['team', id],
        queryFn: () => teamService.getById(id!),
        enabled: isEditing && !!id
    });

    // Lookups
    const { data: confeds } = useQuery({ queryKey: ['confederations'], queryFn: lookupService.getConfederations });
    const { data: countries } = useQuery({ queryKey: ['countries'], queryFn: lookupService.getCountries });
    const { data: regions } = useQuery({
        queryKey: ['regions', formData.pais_origen_id],
        queryFn: () => lookupService.getRegions(formData.pais_origen_id!),
        enabled: !!formData.pais_origen_id
    });
    const { data: cities } = useQuery({
        queryKey: ['cities', formData.pais_origen_id],
        queryFn: () => lookupService.getCities(formData.pais_origen_id!),
        enabled: !!formData.pais_origen_id
    });
    const { data: associations } = useQuery({
        queryKey: ['associations', formData.pais_origen_id],
        queryFn: () => lookupService.getAssociations(formData.pais_origen_id!),
        enabled: !!formData.pais_origen_id
    });
    const { data: stadiums } = useQuery({
        queryKey: ['stadiums', formData.pais_origen_id],
        queryFn: () => lookupService.getStadiums(formData.pais_origen_id),
        enabled: !!formData.pais_origen_id
    });
    const { data: estilos } = useQuery({ queryKey: ['estilos'], queryFn: lookupService.getEstilosJuego });
    const { data: salidas } = useQuery({ queryKey: ['salidas'], queryFn: lookupService.getTiposSalida });
    const { data: transiciones } = useQuery({ queryKey: ['transiciones'], queryFn: () => lookupService.getByDomain('TRANSICION') });
    const { data: tiposPropiedad } = useQuery({ queryKey: ['tipos_propiedad'], queryFn: () => lookupService.getByDomain('TIPO_PROPIEDAD') });
    const { data: estados } = useQuery({ queryKey: ['estados'], queryFn: () => lookupService.getByDomain('ESTADO_GENERICO', 'EQUIPO') });
    const { data: monedas } = useQuery({ queryKey: ['monedas'], queryFn: () => lookupService.getByDomain('MONEDA', 'MONEDA') });

    // Load initial data
    useEffect(() => {
        if (team) {
            console.log('Create/Edit Team Data:', team);
            setFormData({
                nombre: team.nombre,
                mundo_id: team.mundo_id,
                pais_origen_id: team.pais_origen_id,
                ciudad_sede_id: team.ciudad_sede_id,
                asociacion_liga_id: team.asociacion_liga_id,
                estadio_principal_id: team.estadio_principal_id,
                codigo_tla: team.codigo_tla,
                anio_fundacion: team.anio_fundacion,
                estado_id: team.estado_id,
                colores: team.colores,
                elo: team.rating?.elo_actual,
                escudo_media_id: team.escudo_media_id,

                rating: {
                    ataque: team.rating?.ataque ?? 50,
                    defensa: team.rating?.defensa ?? 50,
                    mediocampo: team.rating?.mediocampo ?? 50,
                    moral: team.rating?.moral ?? 50,
                    cohesion: team.rating?.cohesion ?? 50,
                    fatiga: team.rating?.fatiga ?? 0,
                    disciplina: team.rating?.disciplina ?? 50,
                    estilo_id: team.rating?.estilo_id,
                    salida_id: team.rating?.salida_id,
                    transicion_id: team.rating?.transicion_id,
                    tactica_detalle: team.rating?.tactica_detalle || {}
                },
                institucion: team.institucion,
                finanzas: team.finanzas
            });

            // Set Relations
            setDraftRivalries(team.rivalidades || []);
            setDraftStadiumHistory(team.estadio_hist || []);

            // Initialize Cascades
            if (team.pais?.confederacion_id) {
                setSelectedConfed(team.pais.confederacion_id);
            }
            if (team.ciudad_sede?.region?.region_id) {
                setSelectedRegion(team.ciudad_sede.region.region_id);
            } else if (team.ciudad_sede?.region_id) {
                setSelectedRegion(team.ciudad_sede.region_id);
            }
            if (team.escudo_url) {
                setPreviewUrl(`http://127.0.0.1:8000${team.escudo_url}`);
            }
        }
    }, [team]);

    // --- Relations Handlers ---
    const handleAddRivalry = (rivalry: Partial<Rivalidad>) => {
        setDraftRivalries(prev => [...prev, rivalry as Rivalidad]);
    };

    const handleDeleteRivalry = (id: number | string) => {
        if (typeof id === 'number') {
            setRivalriesToDelete(prev => [...prev, id]);
            setDraftRivalries(prev => prev.filter(r => r.rivalidad_id !== id));
        } else {
            // It's a temp ID (string)
            setDraftRivalries(prev => prev.filter(r => !r.rivalidad_id && `temp-${r.equipo_b_id}` !== id));
        }
    };

    const handleAddStadiumHist = (record: Partial<EstadioHist>) => {
        setDraftStadiumHistory(prev => [...prev, { ...record, isNew: true } as any]);
    };

    const handleDeleteStadiumHist = (index: number) => {
        setDraftStadiumHistory(prev => prev.filter((_, i) => i !== index));
    };

    // Derived Lists
    const filteredCountries = selectedConfed
        ? countries?.filter(c => c.confederacion_id === Number(selectedConfed))
        : countries;

    // City/Region Logic
    const filteredCities = selectedRegion
        ? cities?.filter(c => c.region_id === Number(selectedRegion))
        : cities;

    const handleCityChange = (cityId: number) => {
        handleChange('ciudad_sede_id', cityId);
        const city = cities?.find(c => c.ciudad_id === cityId);
        if (city && city.region_id) {
            setSelectedRegion(city.region_id);
        }
    };

    // Mutation
    // Import services for persistence
    const mutation = useMutation({
        mutationFn: async (data: EquipoCreateInput) => {
            let savedTeam: any;
            if (isCreating) {
                savedTeam = await teamService.create(data);
            } else if (id) {
                savedTeam = await teamService.update(id, data);
            } else {
                throw new Error('Invalid operation');
            }

            const teamId = savedTeam.equipo_id;

            // --- Persist Relations ---
            const rivalryService = (await import('@/services/rivalryService')).default;
            const stadiumService = (await import('@/services/stadiumService')).default;

            // 1. Delete Rivalries
            for (const rid of rivalriesToDelete) {
                await rivalryService.delete(rid);
            }

            // 2. Add New Rivalries (the ones without rivalidad_id)
            const newRivalries = draftRivalries.filter(r => !r.rivalidad_id);
            for (const r of newRivalries) {
                await rivalryService.create({
                    ...r,
                    equipo_a_id: teamId
                });
            }

            // 3. Persist Stadium History (only new ones)
            const newStadiumRecords = draftStadiumHistory.filter(s => s.isNew);
            for (const s of newStadiumRecords) {
                await stadiumService.create({
                    ...s,
                    equipo_id: teamId
                } as any);
            }

            return savedTeam;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['teams'] });
            alert('Team and relations saved successfully!');
            router.push('/maintenance/teams');
        },
        onError: (error) => {
            alert('Error saving team: ' + error);
        }
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        mutation.mutate(formData as EquipoCreateInput);
    };

    const handleChange = (field: string, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    // Updated to support deep nesting for tactica_detalle
    const handleTacticChange = (field: string, value: any) => {
        setFormData(prev => ({
            ...prev,
            rating: {
                ...prev.rating,
                [field]: value // stylistic IDs are now top-level in rating object
            } as any
        }));
    };

    const handleTacticDetailChange = (field: string, value: any) => {
        setFormData(prev => ({
            ...prev,
            rating: {
                ...prev.rating,
                tactica_detalle: {
                    ...(prev.rating?.tactica_detalle || {}),
                    [field]: value
                }
            } as any
        }));
    };

    const handleNestedChange = (group: 'rating' | 'institucion' | 'finanzas', field: string, value: any) => {
        // Validation for numeric fields with limits
        if (typeof value === 'number') {
            // Apply specific limits based on group/field
            const rangeFields: string[] = [
                'reputacion_historica',
                'hinchada',
                'infraestructura',
                'estabilidad_directiva',
                'nivel_scouting',
                'nivel_entrenamiento',
                'nivel_juveniles',
                'poder_economico_base',
                'paciencia_directiva'
            ];

            if (rangeFields.includes(field)) {
                if (value < 1) value = 1;
                if (value > 20) value = 20;
            } else if (value < 0) {
                value = 0;
            }
        }

        setFormData(prev => ({
            ...prev,
            [group]: {
                ...(prev[group] || {}),
                [field]: value
            }
        }));
    };

    const formatAmount = (val: number) => {
        return new Intl.NumberFormat('es-PY').format(val || 0);
    };

    const parseFormattedAmount = (str: string) => {
        return parseFloat(str.replace(/\./g, '')) || 0;
    };

    if (isEditing && isLoadingTeam) return (
        <div className="flex items-center justify-center min-h-screen bg-si-900">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-si-accent"></div>
        </div>
    );

    const tabs = [
        { id: 'general', label: 'IDENTITY & LOCATION', icon: Shield },
        { id: 'performance', label: 'PERFORMANCE & TACTICS', icon: Trophy },
        { id: 'finance', label: 'FINANCE & INSTITUTION', icon: MoreHorizontal },
        { id: 'relations', label: 'HISTORY & RELATIONS', icon: MapPin },
    ];

    return (
        <div className="pb-20 min-h-screen bg-si-900 text-gray-100">
            {/* Sticky Header */}
            <div className="sticky top-0 z-30 bg-si-900/80 backdrop-blur-md border-b border-si-800 px-8 py-4 mb-8">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center gap-4">
                        <Link href="/maintenance/teams" className="p-2 hover:bg-si-800 rounded-lg transition-colors text-gray-400 hover:text-white">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div>
                            <h1 className="text-xl font-black tracking-tight uppercase italic flex items-center gap-2">
                                <span className="text-si-accent">{isCreating ? 'NEW' : 'EDIT'}</span>
                                {isCreating ? 'TEAM PROFILE' : team?.nombre}
                            </h1>
                            <p className="text-[10px] text-gray-500 font-bold tracking-widest uppercase">
                                Management Portal / {activeTab.replace('_', ' ')}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => router.push('/maintenance/teams')}
                            className="px-4 py-2 text-sm font-bold text-gray-400 hover:text-white transition-colors"
                        >
                            DISCARD
                        </button>
                        <button
                            onClick={handleSubmit}
                            disabled={mutation.isPending}
                            className="bg-si-accent hover:bg-blue-600 text-white px-8 py-2.5 rounded-lg font-black shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 group disabled:opacity-50"
                        >
                            <Save className="w-5 h-5 group-hover:scale-110 transition-transform" />
                            {isCreating ? 'CREATE TEAM' : 'SAVE CHANGES'}
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-8">
                {/* Tab Navigation */}
                <div className="flex flex-wrap gap-2 mb-8 bg-si-800/30 p-1.5 rounded-xl border border-si-800 w-fit">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        const isActive = activeTab === tab.id;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-xs font-black transition-all tracking-widest uppercase italic ${isActive
                                    ? 'bg-si-accent text-white shadow-lg shadow-blue-500/20'
                                    : 'text-gray-500 hover:text-gray-300 hover:bg-si-800/50'
                                    }`}
                            >
                                <Icon className={`w-4 h-4 ${isActive ? 'animate-pulse' : ''}`} />
                                {tab.label}
                            </button>
                        );
                    })}
                </div>

                <form onSubmit={handleSubmit} className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                    {/* 1. GENERAL TAB */}
                    {activeTab === 'general' && (
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                            {/* Left: Identity */}
                            <div className="lg:col-span-4 space-y-6">
                                <div className="bg-si-800/40 p-6 rounded-2xl border border-si-800 space-y-6">
                                    <h2 className="text-xs font-black text-si-accent tracking-[.3em] uppercase italic">Visual Identity</h2>

                                    <div className="flex flex-col items-center gap-6">
                                        <div className="relative group cross-hair">
                                            <div className="w-40 h-40 bg-si-900 rounded-3xl border-2 border-dashed border-si-700 flex items-center justify-center p-6 relative overflow-hidden group-hover:border-si-accent transition-all cursor-pointer">
                                                {previewUrl ? (
                                                    <img src={previewUrl} alt="Crest" className="w-full h-full object-contain" />
                                                ) : (
                                                    <div className="text-center">
                                                        <Shield className="w-12 h-12 text-si-800 mx-auto mb-2" />
                                                        <span className="text-[10px] text-gray-500 font-bold uppercase">Upload Icon</span>
                                                    </div>
                                                )}
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    onChange={handleImageUpload}
                                                    className="absolute inset-0 opacity-0 cursor-pointer z-10"
                                                />
                                                <div className="absolute inset-0 bg-si-accent/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                                            </div>
                                        </div>

                                        <div className="w-full space-y-4">
                                            <div>
                                                <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1.5 ml-1">Team Colors</label>
                                                <div className="grid grid-cols-3 gap-3">
                                                    {['primario', 'secundario', 'terciario'].map((type) => (
                                                        <div key={type} className="group flex flex-col items-center">
                                                            <div
                                                                className="w-10 h-10 rounded-full border border-si-700 p-0.5 relative cursor-pointer"
                                                                style={{ background: formData.colores?.[type] || '#1f2937' }}
                                                            >
                                                                <input
                                                                    type="color"
                                                                    className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                                                                    value={formData.colores?.[type] || '#ffffff'}
                                                                    onChange={e => handleChange('colores', { ...formData.colores, [type]: e.target.value })}
                                                                />
                                                            </div>
                                                            <span className="text-[8px] font-bold text-gray-600 mt-1 uppercase">{type.slice(0, 4)}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Center/Right: Details & Location */}
                            <div className="lg:col-span-8 space-y-8">
                                <div className="bg-si-800/40 p-8 rounded-2xl border border-si-800 space-y-8">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                        <div className="md:col-span-2">
                                            <label className="block text-[10px] font-black text-si-accent uppercase tracking-widest mb-2 ml-1">Official Club Name</label>
                                            <input
                                                type="text" required
                                                className="w-full bg-si-900 border-si-700 text-white rounded-xl p-4 text-xl font-bold uppercase italic focus:ring-2 focus:ring-si-accent transition-all"
                                                value={formData.nombre || ''}
                                                onChange={e => handleChange('nombre', e.target.value)}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">Short Code (TLA)</label>
                                            <input
                                                type="text" maxLength={10}
                                                className="w-full bg-si-900/50 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent uppercase"
                                                value={formData.codigo_tla || ''}
                                                onChange={e => handleChange('codigo_tla', e.target.value.toUpperCase())}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">Foundation</label>
                                            <input
                                                type="number"
                                                className="w-full bg-si-900/50 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent"
                                                value={formData.anio_fundacion || ''}
                                                onChange={e => handleChange('anio_fundacion', parseInt(e.target.value))}
                                            />
                                        </div>
                                    </div>

                                    <div className="pt-4 border-t border-si-800 space-y-6">
                                        <h3 className="text-[10px] font-black text-si-accent tracking-[.3em] uppercase italic">Geographic Data</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="space-y-4">
                                                <div>
                                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">Confederation</label>
                                                    <select
                                                        value={selectedConfed} onChange={e => setSelectedConfed(Number(e.target.value))}
                                                        className="w-full bg-si-900/50 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent"
                                                    >
                                                        <option value="">All</option>
                                                        {confeds?.map(c => <option key={c.confederacion_id} value={c.confederacion_id}>{c.nombre}</option>)}
                                                    </select>
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">Country</label>
                                                    <select
                                                        required
                                                        value={formData.pais_origen_id || ''}
                                                        onChange={e => {
                                                            const cid = Number(e.target.value);
                                                            handleChange('pais_origen_id', cid);
                                                            handleChange('ciudad_sede_id', undefined);
                                                            setSelectedRegion('');
                                                            const country = countries?.find(c => c.pais_id === cid);
                                                            if (country && country.confederacion_id) setSelectedConfed(country.confederacion_id);
                                                        }}
                                                        className="w-full bg-si-900/50 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent"
                                                    >
                                                        <option value="">Select Country</option>
                                                        {filteredCountries?.map(c => <option key={c.pais_id} value={c.pais_id}>{c.nombre}</option>)}
                                                    </select>
                                                </div>
                                            </div>
                                            <div className="space-y-4">
                                                <div>
                                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">Region</label>
                                                    <select
                                                        value={selectedRegion} onChange={e => setSelectedRegion(Number(e.target.value))} disabled={!formData.pais_origen_id}
                                                        className="w-full bg-si-900/50 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent disabled:opacity-30"
                                                    >
                                                        <option value="">All Regions</option>
                                                        {regions?.map(r => <option key={r.region_id} value={r.region_id}>{r.nombre}</option>)}
                                                    </select>
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 ml-1">City</label>
                                                    <select
                                                        value={formData.ciudad_sede_id || ''} onChange={e => handleCityChange(Number(e.target.value))} disabled={!formData.pais_origen_id}
                                                        className="w-full bg-si-900/50 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent disabled:opacity-30"
                                                    >
                                                        <option value="">Select City</option>
                                                        {filteredCities?.map(c => <option key={c.ciudad_id} value={c.ciudad_id}>{c.nombre}</option>)}
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 2. PERFORMANCE TAB */}
                    {activeTab === 'performance' && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                            {/* ELO & Core Stats */}
                            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
                                <div className="bg-si-accent/10 border border-si-accent/30 p-8 rounded-3xl text-center flex flex-col items-center justify-center space-y-4">
                                    <h3 className="text-[10px] font-black text-si-accent uppercase tracking-[.4em]">Current ELO</h3>
                                    <div className="relative">
                                        <div className="absolute inset-0 bg-si-accent blur-2xl opacity-20" />
                                        <input
                                            type="number"
                                            value={formData.elo ?? 1200}
                                            onChange={e => handleChange('elo', parseFloat(e.target.value))}
                                            className="relative text-6xl font-black italic bg-transparent border-none text-white text-center focus:ring-0 w-full"
                                        />
                                    </div>
                                    <div className="text-[10px] font-bold text-gray-500 uppercase">Competitive Rating</div>
                                </div>

                                <div className="lg:col-span-3 bg-si-800/40 p-8 rounded-3xl border border-si-800 grid grid-cols-1 md:grid-cols-3 gap-8">
                                    {['ataque', 'defensa', 'mediocampo'].map(stat => {
                                        const value = (formData.rating as any)?.[stat] || 50;
                                        return (
                                            <div key={stat} className="space-y-4">
                                                <div className="flex justify-between items-end">
                                                    <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{stat}</label>
                                                    <span className="text-xl font-black italic text-white">{value}</span>
                                                </div>
                                                <div className="relative h-2 bg-si-900 rounded-full overflow-hidden border border-si-700">
                                                    <div
                                                        className={`absolute inset-y-0 left-0 transition-all duration-1000 ${stat === 'ataque' ? 'bg-si-danger' : stat === 'defensa' ? 'bg-si-success' : 'bg-si-accent'
                                                            }`}
                                                        style={{ width: `${value}%` }}
                                                    />
                                                </div>
                                                <input
                                                    type="range" min="0" max="100" value={value}
                                                    onChange={e => handleNestedChange('rating', stat, parseInt(e.target.value))}
                                                    className="w-full accent-si-accent"
                                                />
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Tactics */}
                            <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 space-y-12">
                                <div className="flex justify-between items-center border-b border-si-800 pb-4">
                                    <h2 className="text-xl font-black italic tracking-tight uppercase flex items-center gap-3">
                                        <LayoutGrid className="w-6 h-6 text-si-accent" />
                                        Tactical Configuration
                                    </h2>
                                    <StatusBadge estado={formData.estado_id ? 'CONFIGURED' : 'AUTO'} />
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
                                    {/* Style Group */}
                                    <div className="space-y-8">
                                        <h4 className="text-[10px] font-black text-si-accent uppercase tracking-widest">Philosophy</h4>
                                        <div className="space-y-6">
                                            <div>
                                                <label className="block text-[10px] font-bold text-gray-500 uppercase mb-2">Game Style</label>
                                                <select value={formData.rating?.estilo_id || ''} onChange={e => handleTacticChange('estilo_id', Number(e.target.value))} className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3 text-sm italic">
                                                    <option value="">Default</option>
                                                    {estilos?.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-[10px] font-bold text-gray-500 uppercase mb-2">Transition Phase</label>
                                                <select value={formData.rating?.transicion_id || ''} onChange={e => handleTacticChange('transicion_id', Number(e.target.value))} className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3 text-sm italic">
                                                    <option value="">Default</option>
                                                    {transiciones?.map(t => <option key={t.id} value={t.id}>{t.nombre}</option>)}
                                                </select>
                                            </div>
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-[10px] font-bold text-gray-500">
                                                    <span>WIDTH</span>
                                                    <span>{formData.rating?.tactica_detalle?.anchura ?? 50}%</span>
                                                </div>
                                                <input type="range" min="0" max="100" value={formData.rating?.tactica_detalle?.anchura ?? 50} onChange={e => handleTacticDetailChange('anchura', parseInt(e.target.value))} className="w-full accent-si-accent" />
                                            </div>
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-[10px] font-bold text-gray-500">
                                                    <span>SET PIECES</span>
                                                    <span>{formData.rating?.tactica_detalle?.balon_parado ?? 50}%</span>
                                                </div>
                                                <input type="range" min="0" max="100" value={formData.rating?.tactica_detalle?.balon_parado ?? 50} onChange={e => handleTacticDetailChange('balon_parado', parseInt(e.target.value))} className="w-full accent-si-accent" />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Attack Group */}
                                    <div className="space-y-8">
                                        <h4 className="text-[10px] font-black text-si-accent uppercase tracking-widest">Attacking</h4>
                                        <div className="space-y-6">
                                            <div>
                                                <label className="block text-[10px] font-bold text-gray-500 uppercase mb-2">Build-up Type</label>
                                                <select value={formData.rating?.salida_id || ''} onChange={e => handleTacticChange('salida_id', Number(e.target.value))} className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3 text-sm italic">
                                                    <option value="">Default</option>
                                                    {salidas?.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                                                </select>
                                            </div>
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-[10px] font-bold text-gray-500">
                                                    <span>BUILD-UP TEMPO</span>
                                                    <span>{formData.rating?.tactica_detalle?.ritmo ?? 50}%</span>
                                                </div>
                                                <input type="range" min="0" max="100" value={formData.rating?.tactica_detalle?.ritmo ?? 50} onChange={e => handleTacticDetailChange('ritmo', parseInt(e.target.value))} className="w-full accent-si-accent" />
                                            </div>
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-[10px] font-bold text-gray-500">
                                                    <span>PASSING DIRECTNESS</span>
                                                    <span>{formData.rating?.tactica_detalle?.pases ?? 50}%</span>
                                                </div>
                                                <input type="range" min="0" max="100" value={formData.rating?.tactica_detalle?.pases ?? 50} onChange={e => handleTacticDetailChange('pases', parseInt(e.target.value))} className="w-full accent-si-accent" />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Defense Group */}
                                    <div className="space-y-8">
                                        <h4 className="text-[10px] font-black text-si-accent uppercase tracking-widest">Defensive</h4>
                                        <div className="space-y-6">
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-[10px] font-bold text-gray-500">
                                                    <span>PRESSURE</span>
                                                    <span>{formData.rating?.tactica_detalle?.presion ?? 50}%</span>
                                                </div>
                                                <input type="range" min="0" max="100" value={formData.rating?.tactica_detalle?.presion ?? 50} onChange={e => handleTacticDetailChange('presion', parseInt(e.target.value))} className="w-full accent-si-accent" />
                                            </div>
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-[10px] font-bold text-gray-500">
                                                    <span>AGGRESSION</span>
                                                    <span>{formData.rating?.tactica_detalle?.agresividad ?? 50}%</span>
                                                </div>
                                                <input type="range" min="0" max="100" value={formData.rating?.tactica_detalle?.agresividad ?? 50} onChange={e => handleTacticDetailChange('agresividad', parseInt(e.target.value))} className="w-full accent-si-accent" />
                                            </div>
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-[10px] font-bold text-gray-500">
                                                    <span>DEFENSIVE LINE</span>
                                                    <span>{formData.rating?.tactica_detalle?.linea_defensiva ?? 50}%</span>
                                                </div>
                                                <input type="range" min="0" max="100" value={formData.rating?.tactica_detalle?.linea_defensiva ?? 50} onChange={e => handleTacticDetailChange('linea_defensiva', parseInt(e.target.value))} className="w-full accent-si-accent" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 3. FINANCE TAB */}
                    {activeTab === 'finance' && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-right-4 duration-500">
                            {/* Economic Profile */}
                            <div className="bg-si-800/40 p-8 rounded-3xl border border-si-800 space-y-8">
                                <h2 className="text-[10px] font-black text-si-accent uppercase tracking-[.4em] italic">Financial Profile</h2>
                                <div className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                            <label className="block text-[8px] font-black text-gray-600 uppercase mb-2">Economic Power (1-20)</label>
                                            <div className="flex items-center gap-2">
                                                <input type="number" min="1" max="20" value={formData.finanzas?.poder_economico_base ?? ""} onChange={e => handleNestedChange('finanzas', 'poder_economico_base', parseInt(e.target.value) || 0)} className="bg-transparent border-none p-0 text-xl font-black italic text-white focus:ring-0 w-12" />
                                                <span className="text-gray-600">/ 20</span>
                                            </div>
                                        </div>
                                        <div className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                            <label className="block text-[8px] font-black text-gray-600 uppercase mb-2">Moneda</label>
                                            <select
                                                value={formData.finanzas?.moneda_id ?? ""}
                                                onChange={e => handleNestedChange('finanzas', 'moneda_id', parseInt(e.target.value))}
                                                className="w-full bg-transparent border-none p-0 text-lg font-black italic text-white focus:ring-0"
                                            >
                                                {monedas?.map(m => (
                                                    <option key={m.id} value={m.id} className="bg-si-800">{m.codigo}</option>
                                                ))}
                                            </select>
                                        </div>
                                    </div>

                                    <div className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                        <label className="block text-[8px] font-black text-gray-600 uppercase mb-2">Ownership Type</label>
                                        <select value={formData.finanzas?.tipo_propiedad_id ?? ""} onChange={e => handleNestedChange('finanzas', 'tipo_propiedad_id', parseInt(e.target.value) || undefined)} className="w-full bg-transparent border-none p-0 text-lg font-black italic text-white focus:ring-0">
                                            <option value="" className="bg-si-800">Select...</option>
                                            {tiposPropiedad?.map(t => <option key={t.id} value={t.id} className="bg-si-800">{t.codigo}</option>)}
                                        </select>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                            <label className="block text-[8px] font-black text-gray-600 uppercase mb-2">Transfer Budget</label>
                                            <input
                                                type="text"
                                                value={formatAmount(formData.finanzas?.presupuesto_fichajes || 0)}
                                                onChange={e => handleNestedChange('finanzas', 'presupuesto_fichajes', parseFormattedAmount(e.target.value))}
                                                className="w-full bg-transparent border-none p-0 text-lg font-black italic text-white focus:ring-0"
                                            />
                                        </div>
                                        <div className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                            <label className="block text-[8px] font-black text-gray-600 uppercase mb-2">Wage Budget</label>
                                            <input
                                                type="text"
                                                value={formatAmount(formData.finanzas?.presupuesto_salarial || 0)}
                                                onChange={e => handleNestedChange('finanzas', 'presupuesto_salarial', parseFormattedAmount(e.target.value))}
                                                className="w-full bg-transparent border-none p-0 text-lg font-black italic text-white focus:ring-0"
                                            />
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                            <label className="block text-[8px] font-black text-gray-600 uppercase mb-2">Total Debt</label>
                                            <input
                                                type="text"
                                                value={formatAmount(formData.finanzas?.deuda_total || 0)}
                                                onChange={e => handleNestedChange('finanzas', 'deuda_total', parseFormattedAmount(e.target.value))}
                                                className="w-full bg-transparent border-none p-0 text-lg font-black italic text-white focus:ring-0"
                                            />
                                        </div>
                                        <div className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                            <label className="block text-[8px] font-black text-gray-600 uppercase mb-2">Board Patience (1-20)</label>
                                            <div className="flex items-center gap-2">
                                                <input type="number" min="1" max="20" value={formData.finanzas?.paciencia_directiva ?? ""} onChange={e => handleNestedChange('finanzas', 'paciencia_directiva', parseInt(e.target.value) || 0)} className="bg-transparent border-none p-0 text-xl font-black italic text-white focus:ring-0 w-12" />
                                                <span className="text-gray-600">/ 20</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Institutional Profile */}
                            <div className="bg-si-800/40 p-8 rounded-3xl border border-si-800 space-y-8">
                                <h2 className="text-[10px] font-black text-si-accent uppercase tracking-[.4em] italic">Institutional Stats</h2>
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                                    <div className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                        <label className="block text-[8px] font-black text-gray-600 uppercase mb-2">Potencial Basal</label>
                                        <input type="number" value={(formData.institucion as any)?.potencial_basal ?? ""} onChange={e => handleNestedChange('institucion', 'potencial_basal', parseInt(e.target.value) || 0)} className="w-full bg-transparent border-none p-0 text-lg font-black italic text-white focus:ring-0" />
                                    </div>
                                    {['reputacion_historica', 'hinchada', 'infraestructura', 'estabilidad_directiva', 'nivel_scouting', 'nivel_juveniles'].map(stat => (
                                        <div key={stat} className="bg-si-900/50 p-4 rounded-2xl border border-si-700">
                                            <label className="block text-[8px] font-black text-si-accent uppercase mb-2">{stat.replace('nivel_', '').replace('_', ' ')}</label>
                                            <div className="flex items-center gap-2">
                                                <input type="number" min="0" max="20" value={(formData.institucion as any)?.[stat] ?? ""} onChange={e => handleNestedChange('institucion', stat, parseInt(e.target.value) || 0)} className="bg-transparent border-none p-0 text-xl font-black italic text-white focus:ring-0 w-12" />
                                                <span className="text-gray-600">/ 20</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 4. RELATIONS TAB */}
                    {activeTab === 'relations' && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                            <div className="bg-si-800/40 p-8 rounded-3xl border border-si-800">
                                <RivalryManager
                                    equipoId={id}
                                    rivalries={draftRivalries}
                                    onAdd={handleAddRivalry}
                                    onDelete={handleDeleteRivalry}
                                />
                            </div>
                            <div className="bg-si-800/40 p-8 rounded-3xl border border-si-800">
                                <StadiumManager
                                    equipoId={id}
                                    countryId={formData.pais_origen_id}
                                    history={draftStadiumHistory}
                                    onAdd={handleAddStadiumHist}
                                    onDelete={handleDeleteStadiumHist}
                                />
                            </div>
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
}
