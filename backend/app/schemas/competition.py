from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from datetime import date, datetime

class CompetenciaBase(BaseModel):
    nombre: str
    tipo_id: int
    mundo_id: int
    confederacion_id: Optional[int] = None
    pais_id: Optional[int] = None
    region_id: Optional[int] = None
    asociacion_id: Optional[int] = None
    ciudad_id: Optional[int] = None
    reputacion_base: int = 5000
    configuracion_base: dict = Field(default_factory=dict)
    meta: dict = Field(default_factory=dict)

class CompetenciaCreate(CompetenciaBase):
    pass

class CompetenciaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo_id: Optional[int] = None
    confederacion_id: Optional[int] = None
    pais_id: Optional[int] = None
    region_id: Optional[int] = None
    asociacion_id: Optional[int] = None
    ciudad_id: Optional[int] = None
    reputacion_base: Optional[int] = None
    configuracion_base: Optional[dict] = None
    meta: Optional[dict] = None

class Competencia(CompetenciaBase):
    competencia_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Edicion ---

class CompetenciaEdicionBase(BaseModel):
    competencia_id: int
    temporada_id: int
    nombre_display: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado_id: int = 25 # Default 'PROGRAMADA' (cat_parametro)
    reglas_edicion: dict = Field(default_factory=dict)
    meta: dict = Field(default_factory=dict)

class CompetenciaEdicionCreate(CompetenciaEdicionBase):
    pass

class CompetenciaEdicionUpdate(BaseModel):
    nombre_display: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado_id: Optional[int] = None
    reglas_edicion: Optional[dict] = None
    meta: Optional[dict] = None

class CompetenciaEdicion(CompetenciaEdicionBase):
    edicion_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Etapa ---

class EtapaBase(BaseModel):
    edicion_id: int
    orden: int
    tipo_id: int
    nombre: str
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    config_etapa: dict = Field(default_factory=dict)
    perfil_sorteo_id: Optional[int] = None

class EtapaCreate(EtapaBase):
    pass

class Etapa(EtapaBase):
    etapa_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Grupo ---

class GrupoBase(BaseModel):
    etapa_id: int
    codigo: str
    nombre: Optional[str] = None
    meta: dict = Field(default_factory=dict)

class GrupoCreate(GrupoBase):
    pass

class Grupo(GrupoBase):
    grupo_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Participante ---

class ParticipanteBase(BaseModel):
    edicion_id: int
    equipo_id: int
    metodo_id: Optional[int] = None
    seed: Optional[int] = None
    bombo_sorteo: Optional[int] = None
    grupo_id_inicial: Optional[int] = None
    grupo_inicial_texto: Optional[str] = None
    posicion_final: Optional[int] = None
    ronda_eliminacion: Optional[str] = None
    puntos_ranking_ganados: float = 0.0
    meta: dict = Field(default_factory=dict)

class ParticipanteCreate(ParticipanteBase):
    pass

class Participante(ParticipanteBase):
    participante_id: int
    equipo_nombre: Optional[str] = None # We will populate this manually or via relationship
    model_config = ConfigDict(from_attributes=True)

# --- Tabla de Posiciones ---

class TablaPosicionesBase(BaseModel):
    edicion_id: int
    etapa_id: int
    grupo_id: Optional[int] = None
    equipo_id: int
    pj: int = 0
    pg: int = 0
    pe: int = 0
    pp: int = 0
    gf: int = 0
    gc: int = 0
    dg: int = 0
    pts: int = 0
    forma: Optional[str] = None
    actualizado_en: datetime = Field(default_factory=datetime.now)
    meta: dict = Field(default_factory=dict)

class TablaPosiciones(BaseModel):
    edicion_id: int
    etapa_id: int
    grupo_id: Optional[int] = None
    equipo_id: int
    pj: int
    pg: int
    pe: int
    pp: int
    gf: int
    gc: int
    dg: int
    pts: int
    forma: Optional[str]
    actualizado_en: datetime
    
    model_config = ConfigDict(from_attributes=True)
