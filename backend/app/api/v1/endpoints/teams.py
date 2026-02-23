from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api import deps
from app.schemas.team import Equipo, EquipoCreate, EquipoSummary
from app.core import db
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.team import (
    Equipo as EquipoModel, 
    EquipoRatingActual, 
    EquipoInstitucion, 
    EquipoFinanzas
)
from app.models.common import CatDominio, CatParametro
from app.models.geo import Ciudad

router = APIRouter()

@router.get("/", response_model=List[EquipoSummary])
async def read_equipos(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    pais_id: int = None,
    ciudad_id: int = None,
    confederacion_id: int = None,
    competencia_id: int = None,
    elo_min: int = None,
    elo_max: int = None,
    estado_id: int = None,
    sort_by: str = 'equipo_id',
    sort_desc: bool = False,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Retrieve teams with advanced filtering.
    """
    from app.models.geo import Pais, Confederacion
    from app.models.competition import Participante, CompetenciaEdicion
    from sqlalchemy import desc, asc
    
    stmt = select(EquipoModel)
    
    # 1. Search (Name)
    if search:
        stmt = stmt.where(EquipoModel.nombre.ilike(f"%{search}%"))
        
    # 2. Pais
    if pais_id:
        stmt = stmt.where(EquipoModel.pais_origen_id == pais_id)

    # 3. Ciudad
    if ciudad_id:
        stmt = stmt.where(EquipoModel.ciudad_sede_id == ciudad_id)

    # 4. Estado
    if estado_id:
        stmt = stmt.where(EquipoModel.estado_id == estado_id)
        
    # 5. Confederacion (Join Pais -> Confederacion)
    if confederacion_id:
        stmt = stmt.join(Pais, EquipoModel.pais_origen_id == Pais.pais_id)\
                   .where(Pais.confederacion_id == confederacion_id)

    # 6. Competencia
    if competencia_id:
        stmt = stmt.distinct().join(Participante, EquipoModel.equipo_id == Participante.equipo_id)\
                   .join(CompetenciaEdicion, Participante.edicion_id == CompetenciaEdicion.edicion_id)\
                   .where(CompetenciaEdicion.competencia_id == competencia_id)

    # 7. ELO Range (requires Join with Rating)
    if elo_min is not None or elo_max is not None:
        stmt = stmt.join(EquipoRatingActual, EquipoModel.equipo_id == EquipoRatingActual.equipo_id)
        if elo_min is not None:
            stmt = stmt.where(EquipoRatingActual.elo_actual >= elo_min)
        if elo_max is not None:
            stmt = stmt.where(EquipoRatingActual.elo_actual <= elo_max)

    # Eager load locations for list view
    from app.models.geo import Ciudad
    stmt = stmt.options(
        selectinload(EquipoModel.pais),
        selectinload(EquipoModel.ciudad_sede).selectinload(Ciudad.region),
        selectinload(EquipoModel.rating),
        selectinload(EquipoModel.estado),
        selectinload(EquipoModel.escudo_media)
    )

    # 8. Sorting
    sort_column = None
    if sort_by == 'nombre':
        sort_column = EquipoModel.nombre
    elif sort_by == 'pais_origen_id':
        sort_column = EquipoModel.pais_origen_id
    elif sort_by == 'ciudad_sede_id':
        sort_column = EquipoModel.ciudad_sede_id
    elif sort_by == 'anio_fundacion':
        sort_column = EquipoModel.anio_fundacion
    elif sort_by == 'codigo_tla':
        sort_column = EquipoModel.codigo_tla
    elif sort_by == 'elo': # Sort by ELO
        # Ensure we agreed on joining rating above or here
        # If we didn't join for filter, we need to join for sort or use eager load attribute (but lazy sort won't work easily)
        # Safest is to join if not already joined? 
        # But we can just join cleanly, SQLAlchemy dedupes joins usually if configured right, or we check.
        # Simple approach: Left Outer Join to include teams without rating (treated as clean)
        stmt = stmt.outerjoin(EquipoRatingActual, EquipoModel.equipo_id == EquipoRatingActual.equipo_id)
        sort_column = EquipoRatingActual.elo_actual
    else:
        sort_column = EquipoModel.equipo_id # Default

    if sort_desc:
        stmt = stmt.order_by(desc(sort_column))
    else:
        stmt = stmt.order_by(asc(sort_column))

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{equipo_id}", response_model=Equipo)
async def read_equipo(
    equipo_id: int,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get team by ID with all details.
    """
    from app.models.team import Rivalidad
    from sqlalchemy import or_

    result = await db.execute(
        select(EquipoModel)
        .options(
            selectinload(EquipoModel.rating),
            selectinload(EquipoModel.institucion),
            selectinload(EquipoModel.finanzas),
            selectinload(EquipoModel.estadio_hist),
            selectinload(EquipoModel.pais),
            selectinload(EquipoModel.ciudad_sede).selectinload(Ciudad.region),
            selectinload(EquipoModel.escudo_media)
        )
        .where(EquipoModel.equipo_id == equipo_id)
    )
    equipo = result.scalar_one_or_none()
    if not equipo:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Manually fetch rivalries
    stmt = select(Rivalidad).where(
        or_(Rivalidad.equipo_a_id == equipo_id, Rivalidad.equipo_b_id == equipo_id)
    )
    rivalries_result = await db.execute(stmt)
    equipo.rivalidades = rivalries_result.scalars().all()

    return equipo

@router.post("/", response_model=Equipo)
async def create_equipo(
    equipo_in: EquipoCreate,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Create new team with all nested data.
    """
    # 1. Extract nested data
    rating_data = equipo_in.rating
    institucion_data = equipo_in.institucion
    finanzas_data = equipo_in.finanzas
    
    # 2. Create base team
    team_data = equipo_in.model_dump(exclude={'rating', 'institucion', 'finanzas', 'elo'})
    
    # [REFACTOR] Default state 'ACTIVO' logic
    if not team_data.get('estado_id'):
        state_stmt = select(CatParametro.parametro_id).join(CatDominio).where(
            CatDominio.codigo == 'ESTADO_GENERICO',
            CatParametro.codigo == 'ACTIVO'
        )
        state_res = await db.execute(state_stmt)
        team_data['estado_id'] = state_res.scalar_one_or_none()

    db_team = EquipoModel(**team_data)
    db.add(db_team)
    await db.flush() # Generate ID for relationships

    # 3. Create nested entities (Always create defaults if missing)
    
    # Rating
    r_data = rating_data.model_dump() if rating_data else {}
    # Ensure mandatory defaults for ratings if not provided (though Pydantic handles some)
    if equipo_in.elo is not None:
        r_data['elo_actual'] = equipo_in.elo
    
    db_rating = EquipoRatingActual(equipo_id=db_team.equipo_id, **r_data)
    db.add(db_rating)

    # Institution
    # Mandatory defaults for ranges 1-20: infraestructura, scouting, juveniles, estabilidad, hinchada, reputacion
    i_data = institucion_data.model_dump() if institucion_data else {}
    for field in ['infraestructura', 'nivel_scouting', 'nivel_entrenamiento', 'nivel_juveniles', 'estabilidad_directiva', 'hinchada', 'reputacion_historica']:
        if i_data.get(field) is None:
            i_data[field] = 10
    
    db_inst = EquipoInstitucion(equipo_id=db_team.equipo_id, **i_data)
    db.add(db_inst)

    # Finanzas
    # Mandatory defaults: pod_econ=10, patience=10, budgets/debt=0, moneda_id=52
    f_data = finanzas_data.model_dump() if finanzas_data else {}
    if f_data.get('moneda_id') is None:
        f_data['moneda_id'] = 52 # USD
    if f_data.get('poder_economico_base') is None:
        f_data['poder_economico_base'] = 10
    if f_data.get('paciencia_directiva') is None:
        f_data['paciencia_directiva'] = 10
    
    db_fin = EquipoFinanzas(equipo_id=db_team.equipo_id, **f_data)
    db.add(db_fin)

    await db.commit()
    await db.refresh(db_team)
    
    # Eager load for response
    from app.models.geo import Ciudad
    result = await db.execute(
        select(EquipoModel)
        .options(
            selectinload(EquipoModel.rating),
            selectinload(EquipoModel.institucion),
            selectinload(EquipoModel.finanzas),
            selectinload(EquipoModel.estadio_hist),
            selectinload(EquipoModel.pais),
            selectinload(EquipoModel.ciudad_sede).selectinload(Ciudad.region),
            selectinload(EquipoModel.escudo_media)
        )
        .where(EquipoModel.equipo_id == db_team.equipo_id)
    )
    return result.scalar_one()

@router.put("/{equipo_id}", response_model=Equipo)
async def update_equipo(
    equipo_id: int,
    equipo_in: EquipoCreate,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Update team and nested relations.
    """
    # 1. Get existing team with relations
    stmt = select(EquipoModel).options(
        selectinload(EquipoModel.rating),
        selectinload(EquipoModel.institucion),
        selectinload(EquipoModel.finanzas),
        selectinload(EquipoModel.pais),
        selectinload(EquipoModel.ciudad_sede).selectinload(Ciudad.region)
    ).where(EquipoModel.equipo_id == equipo_id)

    result = await db.execute(stmt)
    db_team = result.scalar_one_or_none()

    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    # 2. Update base fields
    team_data = equipo_in.model_dump(exclude={'rating', 'institucion', 'finanzas', 'elo'}, exclude_unset=True)
    for field, value in team_data.items():
        setattr(db_team, field, value)

    # 3. Update nested
    # Rating
    if equipo_in.rating:
        if not db_team.rating:
            db_team.rating = EquipoRatingActual(equipo_id=equipo_id)

        r_up = equipo_in.rating.model_dump(exclude_unset=True)
        # Handle rename manually if needed, but model_dump(by_alias=True) should help if we used aliases
        # Actually our schema uses tactica_detalle and alias="tactica"
        for field, value in r_up.items():
            setattr(db_team.rating, field, value)

    # If ELO is in root update, update rating too
    if equipo_in.elo is not None:
        if not db_team.rating:
             db_team.rating = EquipoRatingActual(equipo_id=equipo_id)
        db_team.rating.elo_actual = equipo_in.elo

    # Institution
    if equipo_in.institucion:
        if not db_team.institucion:
            db_team.institucion = EquipoInstitucion(equipo_id=equipo_id)
        for field, value in equipo_in.institucion.model_dump(exclude_unset=True).items():
            setattr(db_team.institucion, field, value)

    # Finances
    if equipo_in.finanzas:
         if not db_team.finanzas:
            db_team.finanzas = EquipoFinanzas(equipo_id=equipo_id, moneda_id=52)
         for field, value in equipo_in.finanzas.model_dump(exclude_unset=True).items():
            setattr(db_team.finanzas, field, value)

    await db.commit()
    await db.refresh(db_team)

    # Reload with all data (including new stadium/rivalries if we fetched them, but for UPDATE just returning the main object is usually enough, but let's be consistent)
    # The response model expects all fields.
    # Rivalries and Stadiums are separate lists, usually not updated via PUT /teams/{id} main body, 
    # but we need to populate them for the response schema to be valid or empty.
    
    # Ideally we re-fetch everything
    return await read_equipo(equipo_id, db)

@router.delete("/{equipo_id}")
async def delete_equipo(
    equipo_id: int,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Delete team.
    """
    stmt = select(EquipoModel).where(EquipoModel.equipo_id == equipo_id)
    result = await db.execute(stmt)
    equipo = result.scalar_one_or_none()
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Team not found")
        
    await db.delete(equipo)
    await db.commit()
    return {"message": "Team deleted"}
