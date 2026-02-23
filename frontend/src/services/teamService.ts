import api from '@/lib/api';
import { Equipo, EquipoCreateInput } from '@/types';

export interface TeamFilters {
    search?: string;
    pais_id?: number;
    ciudad_id?: number;
    confederacion_id?: number;
    competencia_id?: number;
    elo_min?: number;
    elo_max?: number;
    estado?: string;
    sort_by?: string;
    sort_desc?: boolean;
}

export const teamService = {
    getAll: async (skip = 0, limit = 50, filters: TeamFilters = {}): Promise<Equipo[]> => {
        const params = new URLSearchParams();
        params.append('skip', String(skip));
        params.append('limit', String(limit));

        if (filters.search) params.append('search', filters.search);
        if (filters.pais_id) params.append('pais_id', String(filters.pais_id));
        if (filters.ciudad_id) params.append('ciudad_id', String(filters.ciudad_id));
        if (filters.confederacion_id) params.append('confederacion_id', String(filters.confederacion_id));
        if (filters.competencia_id) params.append('competencia_id', String(filters.competencia_id));
        if (filters.elo_min) params.append('elo_min', String(filters.elo_min));
        if (filters.elo_max) params.append('elo_max', String(filters.elo_max));
        if (filters.estado) params.append('estado', filters.estado);
        if (filters.sort_by) params.append('sort_by', filters.sort_by);
        if (filters.sort_desc !== undefined) params.append('sort_desc', String(filters.sort_desc));

        const response = await api.get<Equipo[]>(`/teams/?${params.toString()}`);
        return response.data;
    },
    getById: async (id: number): Promise<Equipo> => {
        const response = await api.get<Equipo>(`/teams/${id}`);
        return response.data;
    },
    create: async (data: EquipoCreateInput): Promise<Equipo> => {
        const response = await api.post<Equipo>('/teams/', data);
        return response.data;
    },
    update: async (id: number, data: EquipoCreateInput): Promise<Equipo> => {
        const response = await api.put<Equipo>(`/teams/${id}`, data);
        return response.data;
    },
    delete: async (id: number): Promise<void> => {
        await api.delete(`/teams/${id}`);
    },
    uploadMedia: async (file: File, category?: string): Promise<{ media_id: string, url: string }> => {
        const formData = new FormData();
        formData.append('file', file);
        if (category) {
            formData.append('category', category);
        }
        const response = await api.post<{ media_id: string, url: string }>('/media/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    }
};
