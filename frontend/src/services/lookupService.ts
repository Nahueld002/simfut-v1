import api from '@/lib/api';

export interface Country {
    pais_id: number;
    nombre: string;
    iso_code: string;
    confederacion_id: number;
}

export interface City {
    ciudad_id: number;
    nombre: string;
    region_id: number;
    poblacion?: number;
}

export interface Confederacion {
    confederacion_id: number;
    nombre: string;
    acronimo?: string;
}

export interface Competencia {
    competencia_id: number;
    nombre: string;
    tipo_id: number;
    confederacion_id?: number;
    pais_id?: number;
}

export const lookupService = {
    getCountries: async (): Promise<Country[]> => {
        const response = await api.get<Country[]>('/worlds/countries');
        return response.data;
    },
    getCities: async (countryId: number): Promise<City[]> => {
        const response = await api.get<City[]>(`/worlds/cities/${countryId}`);
        return response.data;
    },
    getTeams: async (): Promise<import('@/types').Equipo[]> => {
        // Optimization: Create a specific endpoint for light list or use getAll with limited fields
        // For now using getAll
        const response = await api.get('/teams/?limit=10000');
        return response.data;
    },
    getStadiums: async (countryId?: number): Promise<{ estadio_id: number, nombre: string }[]> => {
        const params = new URLSearchParams();
        if (countryId) params.append('country_id', String(countryId));
        const response = await api.get<{ estadio_id: number, nombre: string }[]>(`/worlds/stadiums?${params.toString()}`);
        return response.data;
    },
    getConfederations: async (): Promise<Confederacion[]> => {
        const response = await api.get<Confederacion[]>('/worlds/confederations');
        return response.data;
    },
    getCompetitions: async (confederacionId?: number, paisId?: number): Promise<Competencia[]> => {
        const params = new URLSearchParams();
        if (confederacionId) params.append('confederacion_id', String(confederacionId));
        if (paisId) params.append('pais_id', String(paisId));

        const response = await api.get<Competencia[]>(`/worlds/competitions?${params.toString()}`);
        return response.data;
    },
    getRegions: async (countryId: number): Promise<{ region_id: number, nombre: string }[]> => {
        const response = await api.get(`/worlds/regions/${countryId}`);
        return response.data;
    },
    getAssociations: async (countryId?: number, confederationId?: number): Promise<{ asociacion_id: number, nombre: string }[]> => {
        const params = new URLSearchParams();
        if (countryId) params.append('country_id', String(countryId));
        if (confederationId) params.append('confederation_id', String(confederationId));

        const response = await api.get(`/worlds/associations?${params.toString()}`);
        return response.data;
    },
    getByDomain: async (domainCode: string, aplicaA?: string): Promise<{ id: number, codigo: string, nombre: string, descripcion: string }[]> => {
        const params = new URLSearchParams();
        if (aplicaA) params.append('aplica_a', aplicaA);
        const response = await api.get<{ id: number, codigo: string, nombre: string, descripcion: string }[]>(`/lookups/${domainCode}?${params.toString()}`);
        return response.data;
    },
    getEstilosJuego: async () => lookupService.getByDomain('ESTILO_JUEGO'),
    getTiposSalida: async () => lookupService.getByDomain('TIPO_SALIDA')
};
