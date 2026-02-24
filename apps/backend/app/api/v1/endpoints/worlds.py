from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api import deps
from app.schemas.world import Mundo, MundoCreate
from app.models.world import Mundo as MundoModel
from app.crud.base import get_all, create
from app.core import db

router = APIRouter()

@router.get("/", response_model=List[Mundo])
async def read_mundos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Retrieve worlds.
    """
    return await get_all(db, MundoModel, skip=skip, limit=limit)

from app.models.geo import Pais, Ciudad, Region
from app.schemas.geo import Pais as PaisSchema, Ciudad as CiudadSchema
from sqlalchemy import select

@router.get("/countries", response_model=List[PaisSchema])
async def read_countries(
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get all countries for dropdowns.
    """
    result = await db.execute(select(Pais).order_by(Pais.nombre))
    return result.scalars().all()

@router.get("/cities/{country_id}", response_model=List[CiudadSchema])
async def read_cities_by_country(
    country_id: int,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get cities by country ID (via Region).
    """
    result = await db.execute(
        select(Ciudad)
        .join(Region, Ciudad.region_id == Region.region_id)
        .where(Region.pais_id == country_id)
        .order_by(Ciudad.nombre)
    )
    return result.scalars().all()

@router.post("/", response_model=Mundo)
async def create_mundo(
    mundo_in: MundoCreate,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Create new world.
    """
    return await create(db, MundoModel, mundo_in.model_dump())

from app.models.geo import Estadio
from app.schemas.geo import Estadio as EstadioSchema

@router.get("/stadiums", response_model=List[EstadioSchema])
async def read_stadiums(
    country_id: int = None,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get stadiums for dropdowns, optionally filtered by country.
    """
    stmt = select(Estadio)
    if country_id:
        stmt = stmt.join(Ciudad, Estadio.ciudad_id == Ciudad.ciudad_id) \
                   .join(Region, Ciudad.region_id == Region.region_id) \
                   .where(Region.pais_id == country_id)
                   
    result = await db.execute(stmt.order_by(Estadio.nombre))
    return result.scalars().all()

from app.models.geo import Confederacion
from app.schemas.geo import Confederacion as ConfederacionSchema # Need to create this schema
from app.models.competition import Competencia
from app.schemas.competition import Competencia as CompetenciaSchema # Need to create this schema

@router.get("/confederations", response_model=List[ConfederacionSchema])
async def read_confederations(
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get all confederations.
    """
    result = await db.execute(select(Confederacion).order_by(Confederacion.nombre))
    return result.scalars().all()

@router.get("/competitions", response_model=List[CompetenciaSchema])
async def read_competitions(
    confederacion_id: int = None,
    pais_id: int = None,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get competitions with optional filtering.
    """
    stmt = select(Competencia)
    if confederacion_id:
        stmt = stmt.where(Competencia.confederacion_id == confederacion_id)
    if pais_id:
        stmt = stmt.where(Competencia.pais_id == pais_id)
    
    stmt = stmt.order_by(Competencia.nombre)
    result = await db.execute(stmt)
    return result.scalars().all()

from app.models.geo import Region, Asociacion
from app.schemas.geo import Region as RegionSchema, Asociacion as AsociacionSchema

@router.get("/regions/{country_id}", response_model=List[RegionSchema])
async def read_regions_by_country(
    country_id: int,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get regions by country ID.
    """
    result = await db.execute(
        select(Region).where(Region.pais_id == country_id).order_by(Region.nombre)
    )
    return result.scalars().all()

@router.get("/associations", response_model=List[AsociacionSchema])
async def read_associations(
    country_id: int = None,
    confederation_id: int = None,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get associations with optional filtering.
    """
    stmt = select(Asociacion)
    if country_id:
        stmt = stmt.where(Asociacion.pais_id == country_id)
    if confederation_id:
        stmt = stmt.where(Asociacion.confederacion_id == confederation_id)
        
    stmt = stmt.order_by(Asociacion.nombre)
    result = await db.execute(stmt)
    return result.scalars().all()
