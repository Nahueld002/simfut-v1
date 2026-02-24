export interface Mundo {
    mundo_id: number;
    nombre: string;
    fecha_actual: string;
    configuracion_global: Record<string, any>;
}

export interface PaisSummary {
    pais_id: number;
    nombre: string;
    confederacion_id?: number;
}

export interface RegionSummary {
    region_id: number;
    nombre: string;
}

export interface CiudadSummary {
    ciudad_id: number;
    nombre: string;
    region_id?: number;
    region?: RegionSummary;
}

export interface EquipoRating {
    elo_actual: number;
    ataque: number;
    defensa: number;
    mediocampo: number;
    moral: number;
    cohesion: number;
    fatiga: number;
    disciplina: number;
    estilo_id?: number;
    salida_id?: number;
    transicion_id?: number;
    tactica_detalle?: Record<string, any>;
}

export interface EquipoInstitucion {
    reputacion_historica: number;
    hinchada: number;
    infraestructura: number;
    estabilidad_directiva: number;
    nivel_scouting: number;
    nivel_entrenamiento: number;
    nivel_juveniles: number;
    volatilidad: number;
    potencial_basal: number;
}

export interface EquipoFinanzas {
    presupuesto_fichajes: number;
    presupuesto_salarial: number;
    deuda_total: number;
    poder_economico_base: number;
    tipo_propiedad_id?: number;
    moneda_id: number;
    paciencia_directiva: number;
}

export interface EstadioHist {
    equipo_id?: number;
    estadio_id: number;
    fecha_inicio: string; // ISO Date
    fecha_fin?: string;
    motivo?: string;
    es_principal: boolean;
}

export interface Rivalidad {
    rivalidad_id: number;
    equipo_a_id: number;
    equipo_b_id: number;
    nombre?: string;
    intensidad: number;
}

export interface Equipo {
    equipo_id: number;
    mundo_id: number;
    nombre: string;
    estado?: string;
    estado_id: number;
    pais_origen_id?: number;
    ciudad_sede_id?: number;
    asociacion_liga_id?: number;
    estadio_principal_id?: number;
    pais?: PaisSummary;
    ciudad_sede?: CiudadSummary;
    anio_fundacion?: number;
    codigo_tla?: string;
    colores: Record<string, any>;
    elo?: number;
    rating?: EquipoRating;
    institucion?: EquipoInstitucion;
    finanzas?: EquipoFinanzas;
    estadio_hist?: EstadioHist[];
    rivalidades?: Rivalidad[];
    escudo_media_id?: string;
    escudo_url?: string;
}

export interface EquipoCreateInput {
    nombre: string;
    estado_id?: number;
    mundo_id: number;
    pais_origen_id: number;
    codigo_tla?: string;
    anio_fundacion?: number;
    ciudad_sede_id?: number;
    asociacion_liga_id?: number;
    estadio_principal_id?: number;
    colores?: Record<string, any>;
    elo?: number;
    rating?: Omit<EquipoRating, 'elo_actual'>;
    institucion?: EquipoInstitucion;
    finanzas?: EquipoFinanzas;
    escudo_media_id?: string;
}
