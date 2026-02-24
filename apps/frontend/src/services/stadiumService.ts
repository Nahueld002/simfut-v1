import api from '@/lib/api';
import { EstadioHist } from '../types';

export interface EstadioHistCreateInput {
    equipo_id: number;
    estadio_id: number;
    fecha_inicio: string;
    fecha_fin?: string;
    motivo?: string;
    es_principal: boolean;
}

const stadiumService = {
    create: async (data: EstadioHistCreateInput): Promise<EstadioHist> => {
        const response = await api.post('/stadiums/', data);
        return response.data;
    },

    getByTeam: async (equipoId: number): Promise<EstadioHist[]> => {
        const response = await api.get(`/stadiums/team/${equipoId}`);
        return response.data;
    }
};

export default stadiumService;
