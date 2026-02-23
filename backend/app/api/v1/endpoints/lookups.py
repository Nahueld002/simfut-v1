from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api import deps
from app.core import db
from app.models import geo, common
from pydantic import BaseModel

router = APIRouter()

# Schemas
class LookupItem(BaseModel):
    id: int
    nombre: str
    codigo: str = None 
    descripcion: str = None

    class Config:
        from_attributes = True

@router.get("/{dominio_codigo}", response_model=List[LookupItem])
async def get_lookup_by_domain(
    dominio_codigo: str, 
    aplica_a: str = None,
    db: AsyncSession = Depends(db.get_db)
):
    """
    Generic endpoint to fetch parameters for a given domain code.
    """
    stmt = (
        select(common.CatParametro)
        .join(common.CatDominio)
        .where(common.CatDominio.codigo == dominio_codigo)
        .where(common.CatParametro.activo == True)
    )
    
    if aplica_a:
        # PostgreSQL JSONB containment operator '?' check if key exists or array contains value
        # In this case metadatos['aplica_a'] is an array
        stmt = stmt.where(common.CatParametro.metadatos['aplica_a'].contains([aplica_a]))

    stmt = stmt.order_by(common.CatParametro.orden)
    result = await db.execute(stmt)
    return [
        LookupItem(
            id=x.parametro_id,
            nombre=x.descripcion if x.descripcion else x.codigo.replace('_', ' ').title(),
            codigo=x.codigo,
            descripcion=x.descripcion
        ) for x in result.scalars().all()
    ]

@router.get("/estilos-juego", response_model=List[LookupItem], include_in_schema=False)
async def get_estilos_juego(db: AsyncSession = Depends(db.get_db)):
    return await get_lookup_by_domain("ESTILO_JUEGO", db)

@router.get("/tipos-salida", response_model=List[LookupItem], include_in_schema=False)
async def get_tipos_salida(db: AsyncSession = Depends(db.get_db)):
    return await get_lookup_by_domain("TIPO_SALIDA", db)

@router.get("/confederaciones", response_model=List[LookupItem])
async def get_confederations(db: AsyncSession = Depends(db.get_db)):
    result = await db.execute(select(geo.Confederacion).order_by(geo.Confederacion.nombre))
    return [LookupItem(id=x.confederacion_id, nombre=x.nombre) for x in result.scalars().all()]

@router.get("/paises", response_model=List[LookupItem])
async def get_countries(db: AsyncSession = Depends(db.get_db)):
    result = await db.execute(select(geo.Pais).order_by(geo.Pais.nombre))
    return [LookupItem(id=x.pais_id, nombre=x.nombre) for x in result.scalars().all()]

@router.get("/regiones/{pais_id}", response_model=List[LookupItem])
async def get_regions(pais_id: int, db: AsyncSession = Depends(db.get_db)):
    result = await db.execute(select(geo.Region).where(geo.Region.pais_id == pais_id).order_by(geo.Region.nombre))
    return [LookupItem(id=x.region_id, nombre=x.nombre) for x in result.scalars().all()]

@router.get("/ciudades/{pais_id}", response_model=List[LookupItem])
async def get_cities(pais_id: int, db: AsyncSession = Depends(db.get_db)):
    # Note: Cities might be many, usually filter by region too, but for now by country via join if needed or assume flat list if small?
    # Schema has city -> region -> pais. 
    # To filter cities by pais, we join region.
    stmt = select(geo.Ciudad).join(geo.Region).where(geo.Region.pais_id == pais_id).order_by(geo.Ciudad.nombre)
    result = await db.execute(stmt)
    return [LookupItem(id=x.ciudad_id, nombre=x.nombre) for x in result.scalars().all()]
