import api from '@/lib/api';
import { Rivalidad } from '../types';

export interface RivalidadCreateInput {
    equipo_a_id: number;
    equipo_b_id: number;
    nombre?: string;
    intensidad: number;
}

const rivalryService = {
    create: async (data: RivalidadCreateInput): Promise<Rivalidad> => {
        const response = await api.post('/rivalries/', data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/rivalries/${id}`);
    },

    getByTeam: async (equipoId: number): Promise<Rivalidad[]> => {
        const response = await api.get(`/rivalries/team/${equipoId}`);
        return response.data;
    }
};

export default rivalryService;
