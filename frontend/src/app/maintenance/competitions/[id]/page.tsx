'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { competitionService, CompetenciaCreateInput } from '@/services/competitionService';
import { lookupService } from '@/services/lookupService';
import Link from 'next/link';
import {
    Save, ArrowLeft, Trophy,
    Settings, Star, LayoutGrid, Plus, Calendar, Shield
} from 'lucide-react';

const CatalogSelect = ({
    label,
    value,
    onChange,
    options,
    placeholder = "Select...",
    required = false,
    idField = "id",
    labelField = "nombre"
}: {
    label: string,
    value?: number,
    onChange: (val: number) => void,
    options?: any[],
    placeholder?: string,
    required?: boolean,
    idField?: string,
    labelField?: string
}) => (
    <div className="space-y-1.5">
        <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">{label}</label>
        <select
            required={required}
            value={value || ''}
            onChange={e => onChange(Number(e.target.value))}
            className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent italic text-sm"
        >
            <option value="">{placeholder}</option>
            {options?.map(opt => {
                const id = opt[idField];
                const labelText = opt.codigo ? opt.codigo.replaceAll('_', ' ') : opt[labelField];
                return (
                    <option key={id} value={id}>
                        {labelText}
                    </option>
                );
            })}
        </select>
    </div>
);

export default function CompetitionFormPage() {
    const params = useParams();
    const router = useRouter();
    const queryClient = useQueryClient();
    const rawId = params?.id;
    const isCreating = rawId === 'create';
    const id = (!isCreating && rawId) ? Number(rawId) : null;
    const [activeTab, setActiveTab] = useState<'general' | 'reputation' | 'eligibility' | 'editions'>('general');

    const [formData, setFormData] = useState<Partial<CompetenciaCreateInput>>({
        nombre: '',
        tipo_id: undefined,
        mundo_id: 1,
        reputacion_base: 5000,
        configuracion_base: {},
        meta: {}
    });

    // Lookups
    const { data: tipos } = useQuery({ queryKey: ['competencia_tipos'], queryFn: () => lookupService.getByDomain('COMPETENCIA_TIPO') });
    const { data: confeds } = useQuery({ queryKey: ['confederations'], queryFn: lookupService.getConfederations });
    const { data: countries } = useQuery({ queryKey: ['countries'], queryFn: lookupService.getCountries });
    const { data: regions } = useQuery({
        queryKey: ['regions', formData.pais_id],
        queryFn: () => formData.pais_id ? lookupService.getRegions(formData.pais_id) : Promise.resolve([]),
        enabled: !!formData.pais_id
    });
    const { data: associations } = useQuery({
        queryKey: ['associations', formData.pais_id, formData.confederacion_id],
        queryFn: () => lookupService.getAssociations(formData.pais_id, formData.confederacion_id)
    });
    const { data: cities } = useQuery({
        queryKey: ['cities', formData.pais_id],
        queryFn: () => formData.pais_id ? lookupService.getCities(formData.pais_id) : Promise.resolve([]),
        enabled: !!formData.pais_id
    });

    // Derived Filters
    const filteredCountries = formData.confederacion_id
        ? countries?.filter(c => c.confederacion_id === formData.confederacion_id)
        : countries;

    const filteredCities = formData.region_id
        ? cities?.filter(c => c.region_id === formData.region_id)
        : cities;

    // Fetch Competition
    const { data: competition, isLoading } = useQuery({
        queryKey: ['competition', id],
        queryFn: () => competitionService.getById(id!),
        enabled: !!id
    });

    const { data: editions } = useQuery({
        queryKey: ['competition-editions', id],
        queryFn: () => competitionService.getEditions(id!),
        enabled: !!id
    });

    useEffect(() => {
        if (competition) {
            setFormData(competition);
        }
    }, [competition]);

    const mutation = useMutation({
        mutationFn: async (data: CompetenciaCreateInput) => {
            if (isCreating) {
                return await competitionService.create(data);
            } else {
                return await competitionService.update(id!, data);
            }
        },
        onSuccess: (saved) => {
            queryClient.invalidateQueries({ queryKey: ['competitions'] });
            alert('Competition saved successfully!');
            if (isCreating) router.push(`/maintenance/competitions/${saved.competencia_id}`);
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        mutation.mutate(formData as CompetenciaCreateInput);
    };

    if (id && isLoading) return <div className="p-20 text-center text-si-accent animate-pulse font-black uppercase tracking-widest italic">Loading...</div>;

    const tabs = [
        { id: 'general', label: 'General Identity', icon: Settings },
        { id: 'reputation', label: 'Reputation', icon: Star },
        { id: 'eligibility', label: 'Eligibility', icon: Shield },
        { id: 'editions', label: 'Editions', icon: Calendar },
    ];

    return (
        <div className="pb-20 min-h-screen bg-si-900 text-gray-100">
            {/* Header */}
            <div className="sticky top-0 z-30 bg-si-900/80 backdrop-blur-md border-b border-si-800 px-8 py-4 mb-8">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center gap-4">
                        <Link href="/maintenance/competitions" className="p-2 hover:bg-si-800 rounded-lg transition-colors text-gray-400 hover:text-white">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div>
                            <h1 className="text-xl font-black tracking-tight uppercase italic flex items-center gap-2">
                                <span className="text-si-accent">{isCreating ? 'NEW' : 'EDIT'}</span>
                                {isCreating ? 'COMPETITION' : competition?.nombre}
                            </h1>
                        </div>
                    </div>

                    <button
                        onClick={handleSubmit}
                        disabled={mutation.isPending}
                        className="bg-si-accent hover:bg-blue-600 text-white px-8 py-2.5 rounded-lg font-black shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 group disabled:opacity-50"
                    >
                        <Save className="w-5 h-5 group-hover:scale-110 transition-transform" />
                        SAVE CHANGES
                    </button>
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
                                    ? 'bg-si-accent text-white shadow-lg shadow-blue-500/20'
                                    : 'text-gray-500 hover:text-gray-300 hover:bg-si-800/50'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        );
                    })}
                </div>

                <form onSubmit={handleSubmit} className="space-y-8 animate-in fade-in duration-500">
                    {activeTab === 'general' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 space-y-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="md:col-span-2">
                                    <label className="block text-[10px] font-black text-si-accent uppercase tracking-widest mb-2 ml-1">Competition Name</label>
                                    <input
                                        type="text" required
                                        className="w-full bg-si-900 border-si-700 text-white rounded-xl p-4 text-xl font-bold uppercase italic focus:ring-2 focus:ring-si-accent transition-all"
                                        value={formData.nombre || ''}
                                        onChange={e => setFormData({ ...formData, nombre: e.target.value })}
                                        placeholder="E.g. COPA LIBERTADORES"
                                    />
                                </div>
                                <CatalogSelect
                                    label="Competition Type"
                                    value={formData.tipo_id}
                                    options={tipos}
                                    onChange={val => setFormData({ ...formData, tipo_id: val })}
                                    required
                                />
                                <div className="space-y-1.5">
                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Base Reputation</label>
                                    <input
                                        type="number"
                                        className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent"
                                        value={formData.reputacion_base || 5000}
                                        onChange={e => setFormData({ ...formData, reputacion_base: parseInt(e.target.value) })}
                                    />
                                </div>
                            </div>

                            <div className="pt-8 border-t border-si-800">
                                <h3 className="text-xs font-black text-si-accent tracking-[.3em] uppercase italic mb-6">Scope & Reach</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <CatalogSelect
                                        label="Confederation"
                                        value={formData.confederacion_id}
                                        options={confeds}
                                        idField="confederacion_id"
                                        onChange={val => setFormData({ ...formData, confederacion_id: val, pais_id: undefined, region_id: undefined, ciudad_id: undefined, asociacion_id: undefined })}
                                    />
                                    <CatalogSelect
                                        label="Country"
                                        value={formData.pais_id}
                                        options={filteredCountries}
                                        idField="pais_id"
                                        onChange={val => {
                                            const country = countries?.find(c => c.pais_id === val);
                                            setFormData({
                                                ...formData,
                                                pais_id: val,
                                                confederacion_id: country?.confederacion_id || formData.confederacion_id,
                                                region_id: undefined,
                                                ciudad_id: undefined,
                                                asociacion_id: undefined
                                            });
                                        }}
                                    />
                                    <CatalogSelect
                                        label="Region"
                                        value={formData.region_id}
                                        options={regions}
                                        idField="region_id"
                                        onChange={val => setFormData({ ...formData, region_id: val, ciudad_id: undefined, asociacion_id: undefined })}
                                    />
                                    <CatalogSelect
                                        label="City"
                                        value={formData.ciudad_id}
                                        options={filteredCities}
                                        idField="ciudad_id"
                                        onChange={val => {
                                            const city = cities?.find(c => c.ciudad_id === val);
                                            setFormData({
                                                ...formData,
                                                ciudad_id: val,
                                                region_id: city?.region_id || formData.region_id
                                            });
                                        }}
                                    />
                                    <CatalogSelect
                                        label="Association"
                                        value={formData.asociacion_id}
                                        options={associations}
                                        idField="asociacion_id"
                                        onChange={val => setFormData({ ...formData, asociacion_id: val })}
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'reputation' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 space-y-8">
                            <div className="flex items-center gap-4 mb-4">
                                <Star className="w-10 h-10 text-yellow-400" />
                                <div>
                                    <h2 className="text-xl font-black italic uppercase">Reputation & Prestige</h2>
                                    <p className="text-gray-500 text-xs font-bold uppercase tracking-widest">Manage how this competition is perceived globally</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-1.5">
                                    <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Current Base Reputation</label>
                                    <input
                                        type="number"
                                        className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent"
                                        value={formData.reputacion_base || 5000}
                                        onChange={e => setFormData({ ...formData, reputacion_base: parseInt(e.target.value) })}
                                    />
                                    <p className="text-[10px] text-gray-600 italic px-1">Initial prestige value for new seasons and team interest.</p>
                                </div>

                                <div className="bg-si-900/50 p-6 rounded-2xl border border-si-700">
                                    <h4 className="text-[10px] font-black text-si-accent uppercase tracking-[.2em] mb-3">Dynamic Adjustments</h4>
                                    <div className="space-y-3">
                                        <label className="flex items-center gap-3 cursor-pointer group">
                                            <input type="checkbox" className="w-4 h-4 rounded border-si-700 bg-si-900 text-si-accent" />
                                            <span className="text-xs font-bold text-gray-400 group-hover:text-white transition-colors uppercase">Enable Seasonal Growth</span>
                                        </label>
                                        <label className="flex items-center gap-3 cursor-pointer group">
                                            <input type="checkbox" className="w-4 h-4 rounded border-si-700 bg-si-900 text-si-accent" />
                                            <span className="text-xs font-bold text-gray-400 group-hover:text-white transition-colors uppercase">Global Reach Bonus</span>
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'eligibility' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 space-y-8">
                            <div className="flex items-center gap-4 mb-4">
                                <Shield className="w-10 h-10 text-si-accent" />
                                <div>
                                    <h2 className="text-xl font-black italic uppercase">Eligibility Rules</h2>
                                    <p className="text-gray-500 text-xs font-bold uppercase tracking-widest">Entry requirements and participant constraints</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-4">
                                    <h4 className="text-[10px] font-black text-si-accent uppercase tracking-[.2em]">Mandatory Requirements</h4>
                                    <div className="space-y-4">
                                        <CatalogSelect
                                            label="Minimum Team Reputation"
                                            value={formData.configuracion_base?.min_rep || 0}
                                            options={[
                                                { id: 0, nombre: 'No Limit' },
                                                { id: 2000, nombre: 'Regional (2000+)' },
                                                { id: 4000, nombre: 'Professional (4000+)' },
                                                { id: 6000, nombre: 'Elite (6000+)' },
                                            ]}
                                            onChange={val => setFormData({
                                                ...formData,
                                                configuracion_base: { ...formData.configuracion_base, min_rep: val }
                                            })}
                                        />
                                        <div className="space-y-1.5">
                                            <label className="block text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Maximum Participants</label>
                                            <input
                                                type="number"
                                                className="w-full bg-si-900 border-si-700 text-white rounded-xl p-3 focus:ring-2 focus:ring-si-accent"
                                                value={formData.configuracion_base?.max_teams || 20}
                                                onChange={e => setFormData({
                                                    ...formData,
                                                    configuracion_base: { ...formData.configuracion_base, max_teams: parseInt(e.target.value) }
                                                })}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-si-900/50 p-8 rounded-2xl border border-si-700 space-y-6">
                                    <h4 className="text-[10px] font-black text-white uppercase tracking-[.2em] flex items-center gap-2">
                                        <LayoutGrid className="w-4 h-4 text-si-accent" />
                                        Automatic Eligibility
                                    </h4>
                                    <div className="space-y-4">
                                        <p className="text-[10px] text-gray-500 leading-relaxed font-bold uppercase">
                                            Teams from the selected <span className="text-white">Scope & Reach</span> will be prioritized during edition generation.
                                        </p>
                                        <div className="flex flex-wrap gap-2">
                                            <span className="px-2 py-1 bg-si-800 text-gray-400 rounded text-[9px] font-black uppercase tracking-tighter">Strict Geography</span>
                                            <span className="px-2 py-1 bg-si-800 text-gray-400 rounded text-[9px] font-black uppercase tracking-tighter">Active Status Only</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'editions' && (
                        <div className="bg-si-800/40 p-10 rounded-3xl border border-si-800 space-y-6">
                            <div className="flex justify-between items-center">
                                <h2 className="text-xl font-black italic uppercase">Competition Editions</h2>
                                {!isCreating && (
                                    <button
                                        type="button"
                                        onClick={() => {
                                            const seasonStr = prompt("Enter season ID (number):", "1");
                                            if (seasonStr) {
                                                competitionService.createEdition({
                                                    competencia_id: id!,
                                                    temporada_id: parseInt(seasonStr),
                                                    nombre_display: `${formData.nombre} - ${new Date().getFullYear()}`,
                                                    estado_id: 25
                                                }).then(() => queryClient.invalidateQueries({ queryKey: ['competition-editions'] }));
                                            }
                                        }}
                                        className="bg-si-accent/10 border border-si-accent/30 text-si-accent px-4 py-2 rounded-lg text-xs font-black uppercase hover:bg-si-accent hover:text-white transition-all flex items-center gap-2"
                                    >
                                        <Plus className="w-4 h-4" />
                                        NEW EDITION
                                    </button>
                                )}
                            </div>

                            <div className="space-y-4">
                                {editions?.map(ed => (
                                    <Link
                                        key={ed.edicion_id}
                                        href={`/maintenance/competition-editions/${ed.edicion_id}`}
                                        className="flex items-center justify-between p-4 bg-si-900/50 rounded-xl border border-si-700 hover:border-si-accent transition-all group"
                                    >
                                        <div>
                                            <p className="font-bold text-white group-hover:text-si-accent transition-colors">
                                                {ed.nombre_display || `Edition ID: ${ed.edicion_id}`}
                                            </p>
                                            <p className="text-[10px] text-gray-500 font-medium uppercase tracking-widest mt-0.5">
                                                Season {ed.temporada_id} • Status ID: {ed.estado_id}
                                            </p>
                                        </div>
                                        <ArrowLeft className="w-5 h-5 text-gray-600 rotate-180 group-hover:text-si-accent transition-colors" />
                                    </Link>
                                ))}
                                {editions?.length === 0 && <p className="text-center text-gray-500 italic py-10">No editions created yet.</p>}
                                {isCreating && <p className="text-center text-gray-500 italic py-10">Save competition first to manage editions.</p>}
                            </div>
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
}
