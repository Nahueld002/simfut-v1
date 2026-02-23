from pydantic import BaseModel
from typing import Optional
from datetime import date
from pydantic import ConfigDict

class MundoBase(BaseModel):
    nombre: str
    semilla_rng: Optional[int] = None
    configuracion_global: dict = {}

class MundoCreate(MundoBase):
    pass

class MundoUpdate(MundoBase):
    nombre: Optional[str] = None

class MundoInDBBase(MundoBase):
    mundo_id: int
    fecha_actual: date

    model_config = ConfigDict(from_attributes=True)

class Mundo(MundoInDBBase):
    pass
