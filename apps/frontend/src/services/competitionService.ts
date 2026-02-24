import api from '@/lib/api';

export interface Competencia {
    competencia_id: number;
    mundo_id: number;
    nombre: string;
    tipo_id: number;
    confederacion_id?: number;
    pais_id?: number;
    region_id?: number;
    asociacion_id?: number;
    ciudad_id?: number;
    reputacion_base: number;
    configuracion_base: any;
    meta: any;
}

export interface CompetenciaCreateInput {
    nombre: string;
    tipo_id: number;
    mundo_id: number;
    confederacion_id?: number;
    pais_id?: number;
    region_id?: number;
    asociacion_id?: number;
    ciudad_id?: number;
    reputacion_base?: number;
    configuracion_base?: any;
    meta?: any;
}

export interface CompetenciaEdicion {
    edicion_id: number;
    competencia_id: number;
    temporada_id: number;
    nombre_display?: string;
    fecha_inicio?: string;
    fecha_fin?: string;
    estado_id: number;
    reglas_edicion: any;
    meta: any;
}

export interface CompetenciaEdicionCreateInput {
    competencia_id: number;
    temporada_id: number;
    nombre_display?: string;
    fecha_inicio?: string;
    fecha_fin?: string;
    estado_id?: number;
    reglas_edicion?: any;
    meta?: any;
}

export interface Etapa {
    etapa_id: number;
    edicion_id: number;
    orden: number;
    tipo_id: number;
    nombre: string;
    fecha_inicio?: string;
    fecha_fin?: string;
    config_etapa: any;
}

export interface Participante {
    participante_id: number;
    edicion_id: number;
    equipo_id: number;
    metodo_id?: number;
    seed?: number;
    bombo_sorteo?: number;
}

export const competitionService = {
    getAll: async (skip = 0, limit = 100, mundo_id?: number): Promise<Competencia[]> => {
        const params = new URLSearchParams();
        params.append('skip', String(skip));
        params.append('limit', String(limit));
        if (mundo_id) params.append('mundo_id', String(mundo_id));
        const response = await api.get<Competencia[]>(`/competitions/?${params.toString()}`);
        return response.data;
    },
    getById: async (id: number): Promise<Competencia> => {
        const response = await api.get<Competencia>(`/competitions/${id}`);
        return response.data;
    },
    create: async (data: CompetenciaCreateInput): Promise<Competencia> => {
        const response = await api.post<Competencia>('/competitions/', data);
        return response.data;
    },
    update: async (id: number, data: Partial<CompetenciaCreateInput>): Promise<Competencia> => {
        const response = await api.patch<Competencia>(`/competitions/${id}`, data);
        return response.data;
    },
    getEditions: async (competitionId: number): Promise<CompetenciaEdicion[]> => {
        const response = await api.get<CompetenciaEdicion[]>(`/competitions/${competitionId}/editions`);
        return response.data;
    },
    createEdition: async (data: CompetenciaEdicionCreateInput): Promise<CompetenciaEdicion> => {
        const response = await api.post<CompetenciaEdicion>('/competitions/editions', data);
        return response.data;
    },
    getEditionById: async (id: number): Promise<CompetenciaEdicion> => {
        const response = await api.get<CompetenciaEdicion>(`/competitions/editions/${id}`);
        return response.data;
    },
    updateEdition: async (id: number, data: Partial<CompetenciaEdicionCreateInput>): Promise<CompetenciaEdicion> => {
        const response = await api.patch<CompetenciaEdicion>(`/competitions/editions/${id}`, data);
        return response.data;
    },
    syncStages: async (editionId: number, stages: any[]): Promise<any> => {
        const response = await api.post(`/competitions/editions/${editionId}/stages/sync`, stages);
        return response.data;
    },
    syncParticipants: async (editionId: number, participants: any[]): Promise<any> => {
        const response = await api.post(`/competitions/editions/${editionId}/participants/sync`, participants);
        return response.data;
    },
    generateFixture: async (editionId: number): Promise<any> => {
        const response = await api.post(`/competitions/editions/${editionId}/generate-fixture`);
        return response.data;
    },
    getStages: async (editionId: number): Promise<Etapa[]> => {
        const response = await api.get<Etapa[]>(`/competitions/editions/${editionId}/stages`);
        return response.data;
    },
    getParticipants: async (editionId: number): Promise<any[]> => {
        const response = await api.get<any[]>(`/competitions/editions/${editionId}/participants`);
        return response.data;
    }
};
