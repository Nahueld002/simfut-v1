from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any, List
from datetime import date
from pydantic import ConfigDict, computed_field
from app.schemas.geo import Pais, CiudadWithRegion
from app.schemas.common import MediaAsset

# --- Nested Schemas ---

# --- Nested Schemas ---

class EquipoRatingCreate(BaseModel):
    ataque: int = Field(50, ge=1, le=100)
    defensa: int = Field(50, ge=1, le=100)
    mediocampo: int = Field(50, ge=1, le=100)
    moral: int = Field(50, ge=0, le=100)
    cohesion: int = Field(50, ge=0, le=100)
    disciplina: int = Field(50, ge=0, le=100)
    fatiga: int = Field(0, ge=0, le=100)
    
    # Tactict IDs
    estilo_id: Optional[int] = None
    salida_id: Optional[int] = None
    transicion_id: Optional[int] = None
    
    tactica_detalle: Optional[dict] = Field(None)
    
    model_config = ConfigDict(populate_by_name=True)

class EquipoInstitucionCreate(BaseModel):
    reputacion_historica: int = Field(10, ge=1, le=20)
    hinchada: int = Field(10, ge=1, le=20)
    infraestructura: int = Field(10, ge=1, le=20)
    estabilidad_directiva: int = Field(10, ge=1, le=20)
    nivel_scouting: int = Field(10, ge=1, le=20)
    nivel_entrenamiento: int = Field(10, ge=1, le=20)
    nivel_juveniles: int = Field(10, ge=1, le=20)
    volatilidad: int = Field(50, ge=1, le=100)
    potencial_basal: int = Field(1200, ge=1)

class EquipoFinanzasCreate(BaseModel):
    presupuesto_fichajes: float = 0
    presupuesto_salarial: float = 0
    deuda_total: float = 0
    poder_economico_base: int = Field(10, ge=1, le=20)
    tipo_propiedad_id: Optional[int] = None
    paciencia_directiva: int = Field(10, ge=1, le=20)
    moneda_id: int = Field(52) # Default USD

# --- Main Link Schemas ---

from uuid import UUID

class EquipoBase(BaseModel):
    nombre: str
    codigo_tla: Optional[str] = None
    anio_fundacion: Optional[int] = None
    estado_id: Optional[int] = None
    elo: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    colores: dict = {}
    meta: dict = {}
    # Link fields
    pais_origen_id: Optional[int] = None
    ciudad_sede_id: Optional[int] = None
    asociacion_liga_id: Optional[int] = None
    estadio_principal_id: Optional[int] = None
    escudo_media_id: Optional[UUID] = None

class EquipoCreate(EquipoBase):
    mundo_id: int
    pais_origen_id: int
    ciudad_sede_id: Optional[int] = None
    
    # Nested Data
    rating: Optional[EquipoRatingCreate] = None
    institucion: Optional[EquipoInstitucionCreate] = None
    finanzas: Optional[EquipoFinanzasCreate] = None

class EquipoUpdate(EquipoBase):
    nombre: Optional[str] = None
    mundo_id: Optional[int] = None
    
class EquipoIndDBNested(BaseModel):
    """Schema for nested responses"""
    elo_actual: float
    ataque: int
    defensa: int
    mediocampo: int

# --- Response Schemas ---

class EquipoRating(BaseModel):
    elo_actual: float
    ataque: int
    defensa: int
    mediocampo: int
    moral: int
    cohesion: int
    disciplina: int
    fatiga: int
    
    estilo_id: Optional[int] = None
    salida_id: Optional[int] = None
    transicion_id: Optional[int] = None
    
    tactica_detalle: Optional[dict] = None
    
    @field_validator('elo_actual', mode='before')
    @classmethod
    def check_elo(cls, v):
        if v is None or (isinstance(v, float) and v != v): # NaN check
            return 1200.0
        return v

    model_config = ConfigDict(from_attributes=True)

class EquipoInstitucion(BaseModel):
    reputacion_historica: int
    hinchada: int
    infraestructura: int
    estabilidad_directiva: int
    nivel_scouting: int
    nivel_entrenamiento: int
    nivel_juveniles: int
    volatilidad: int
    potencial_basal: int
    model_config = ConfigDict(from_attributes=True)

class EquipoFinanzas(BaseModel):
    presupuesto_fichajes: float
    presupuesto_salarial: float
    deuda_total: float
    poder_economico_base: int
    tipo_propiedad_id: Optional[int] = None
    paciencia_directiva: int
    moneda_id: int
    model_config = ConfigDict(from_attributes=True)

class EstadioHistSchema(BaseModel):
    estadio_id: int
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    motivo: Optional[str] = None
    es_principal: bool
    model_config = ConfigDict(from_attributes=True)

class RivalidadSchema(BaseModel):
    rivalidad_id: int
    equipo_a_id: int
    equipo_b_id: int
    nombre: Optional[str] = None
    intensidad: int
    model_config = ConfigDict(from_attributes=True)

class EquipoInDBBase(EquipoBase):
    equipo_id: int
    mundo_id: int
    
    pais: Optional[Pais] = None
    ciudad_sede: Optional[CiudadWithRegion] = None
    
    model_config = ConfigDict(from_attributes=True)

class EquipoSummary(EquipoInDBBase):
    """Lighter schema for list views"""
    rating: Optional[EquipoRating] = None
    estado: Optional[str] = None
    escudo_media: Optional[MediaAsset] = None
    
    @field_validator('estado', mode='before')
    @classmethod
    def get_estado_from_relation(cls, v: Any) -> Any:
        if hasattr(v, 'codigo'):
             return v.codigo
        return v

    @computed_field
    def escudo_url(self) -> Optional[str]:
        if self.escudo_media:
            return self.escudo_media.url
        return None

class Equipo(EquipoInDBBase):
    rating: Optional[EquipoRating] = None
    institucion: Optional[EquipoInstitucion] = None
    finanzas: Optional[EquipoFinanzas] = None
    estadio_hist: List[EstadioHistSchema] = []
    rivalidades: List[RivalidadSchema] = []
    escudo_media: Optional[MediaAsset] = None

    @computed_field
    def escudo_url(self) -> Optional[str]:
        if self.escudo_media:
            return self.escudo_media.url
        return None

Equipo.model_rebuild()
