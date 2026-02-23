from pydantic import BaseModel, ConfigDict
from typing import Optional

class PaisBase(BaseModel):
    nombre: str
    iso_code: str
    
class Pais(PaisBase):
    pais_id: int
    confederacion_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class CiudadBase(BaseModel):
    nombre: str
    poblacion: Optional[int] = None

class Ciudad(CiudadBase):
    ciudad_id: int
    region_id: int
    
    model_config = ConfigDict(from_attributes=True)

class CiudadWithRegion(Ciudad):
    region: Optional['Region'] = None

class EstadioBase(BaseModel):
    nombre: str
    capacidad: int
    ciudad_id: Optional[int] = None
    tipo_cesped_id: Optional[int] = None

class Estadio(EstadioBase):
    estadio_id: int
    
    model_config = ConfigDict(from_attributes=True)

class ConfederacionBase(BaseModel):
    nombre: str
    acronimo: Optional[str] = None

class Confederacion(ConfederacionBase):
    confederacion_id: int
    
    
    model_config = ConfigDict(from_attributes=True)

class RegionBase(BaseModel):
    nombre: str
    pais_id: int

class Region(RegionBase):
    region_id: int
    model_config = ConfigDict(from_attributes=True)

class AsociacionBase(BaseModel):
    nombre: str
    acronimo: Optional[str] = None
    pais_id: Optional[int] = None
    confederacion_id: Optional[int] = None

class Asociacion(AsociacionBase):
    asociacion_id: int
    model_config = ConfigDict(from_attributes=True)
