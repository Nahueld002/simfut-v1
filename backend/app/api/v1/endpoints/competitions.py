from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from app.api import deps
from app.core import db
from app.models.competition import Competencia as CompetenciaModel, CompetenciaEdicion as EdicionModel, Etapa as EtapaModel, Grupo as GrupoModel, Participante as ParticipanteModel
from app.models.match import Partido as PartidoModel
from app.schemas.competition import (
    Competencia, CompetenciaCreate, CompetenciaUpdate,
    CompetenciaEdicion, CompetenciaEdicionCreate, CompetenciaEdicionUpdate,
    EtapaCreate, ParticipanteCreate
)

router = APIRouter()

@router.get("/", response_model=List[Competencia])
async def read_competitions(
    skip: int = 0,
    limit: int = 100,
    mundo_id: int = None,
    db: AsyncSession = Depends(db.get_db)
):
    stmt = select(CompetenciaModel).offset(skip).limit(limit)
    if mundo_id:
        stmt = stmt.where(CompetenciaModel.mundo_id == mundo_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=Competencia, status_code=status.HTTP_201_CREATED)
async def create_competition(
    competition_in: CompetenciaCreate,
    db: AsyncSession = Depends(db.get_db)
):
    new_comp = CompetenciaModel(**competition_in.model_dump())
    db.add(new_comp)
    await db.commit()
    await db.refresh(new_comp)
    return new_comp

@router.get("/{competition_id}", response_model=Competencia)
async def read_competition(
    competition_id: int,
    db: AsyncSession = Depends(db.get_db)
):
    stmt = select(CompetenciaModel).where(CompetenciaModel.competencia_id == competition_id)
    result = await db.execute(stmt)
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    return comp

@router.patch("/{competition_id}", response_model=Competencia)
async def update_competition(
    competition_id: int,
    competition_in: CompetenciaUpdate,
    db: AsyncSession = Depends(db.get_db)
):
    stmt = select(CompetenciaModel).where(CompetenciaModel.competencia_id == competition_id)
    result = await db.execute(stmt)
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    update_data = competition_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comp, field, value)
    
    await db.commit()
    await db.refresh(comp)
    return comp

# --- Ediciones ---

@router.get("/{competition_id}/editions", response_model=List[CompetenciaEdicion])
async def read_competition_editions(
    competition_id: int,
    db: AsyncSession = Depends(db.get_db)
):
    stmt = select(EdicionModel).where(EdicionModel.competencia_id == competition_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/editions", response_model=CompetenciaEdicion, status_code=status.HTTP_201_CREATED)
async def create_competition_edition(
    edicion_in: CompetenciaEdicionCreate,
    db: AsyncSession = Depends(db.get_db)
):
    new_ed = EdicionModel(**edicion_in.model_dump())
    db.add(new_ed)
    await db.commit()
    await db.refresh(new_ed)
    return new_ed

@router.get("/editions/{edicion_id}", response_model=CompetenciaEdicion)
async def read_competition_edition(
    edicion_id: int,
    db: AsyncSession = Depends(db.get_db)
):
    stmt = select(EdicionModel).where(EdicionModel.edicion_id == edicion_id)
    result = await db.execute(stmt)
    ed = result.scalar_one_or_none()
@router.patch("/editions/{edicion_id}", response_model=CompetenciaEdicion)
async def update_competition_edition(
    edicion_id: int,
    edicion_in: CompetenciaEdicionUpdate,
    db: AsyncSession = Depends(db.get_db)
):
    stmt = select(EdicionModel).where(EdicionModel.edicion_id == edicion_id)
    result = await db.execute(stmt)
    ed = result.scalar_one_or_none()
    if not ed:
        raise HTTPException(status_code=404, detail="Edition not found")
    
    update_data = edicion_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ed, field, value)
    
    await db.commit()
    await db.refresh(ed)
    return ed

from app.schemas.competition import Etapa as EtapaSchema, Participante as ParticipanteSchema

@router.get("/editions/{edicion_id}/stages", response_model=List[EtapaSchema])
async def read_edition_stages(
    edicion_id: int,
    db: AsyncSession = Depends(db.get_db)
):
    stmt = select(EtapaModel).where(EtapaModel.edicion_id == edicion_id).order_by(EtapaModel.orden)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/editions/{edicion_id}/participants", response_model=List[ParticipanteSchema])
async def read_edition_participants(
    edicion_id: int,
    db: AsyncSession = Depends(db.get_db)
):
    stmt = select(ParticipanteModel).where(ParticipanteModel.edicion_id == edicion_id)
    result = await db.execute(stmt)
    return result.scalars().all()

# --- Sync & Logic ---

@router.post("/editions/{edicion_id}/stages/sync")
async def sync_stages(
    edicion_id: int,
    stages_in: List[EtapaCreate],
    db: AsyncSession = Depends(db.get_db)
):
    # Delete existing stages (cascades to groups/rondas)
    await db.execute(delete(EtapaModel).where(EtapaModel.edicion_id == edicion_id))
    
    for s in stages_in:
        new_stage = EtapaModel(**s.model_dump())
        db.add(new_stage)
    
    await db.commit()
    return {"status": "success", "message": "Stages synced"}

@router.post("/editions/{edicion_id}/participants/sync")
async def sync_participants(
    edicion_id: int,
    participants_in: List[ParticipanteCreate],
    db: AsyncSession = Depends(db.get_db)
):
    # Delete existing participants
    await db.execute(delete(ParticipanteModel).where(ParticipanteModel.edicion_id == edicion_id))
    
    for p in participants_in:
        new_p = ParticipanteModel(**p.model_dump())
        db.add(new_p)
    
    await db.commit()
    return {"status": "success", "message": "Participants synced"}

@router.post("/editions/{edicion_id}/generate-fixture")
async def generate_fixture(
    edicion_id: int,
    db: AsyncSession = Depends(db.get_db)
):
    # Basic Round-Robin logic (placeholder for now)
    # 1. Fetch participants
    stmt = select(ParticipanteModel).where(ParticipanteModel.edicion_id == edicion_id)
    result = await db.execute(stmt)
    participants = result.scalars().all()
    
    if len(participants) < 2:
        raise HTTPException(status_code=400, detail="At least 2 participants needed")
    
    # 2. Fetch first stage (assume ID 1 or lowest order)
    stmt = select(EtapaModel).where(EtapaModel.edicion_id == edicion_id).order_by(EtapaModel.orden)
    result = await db.execute(stmt)
    stage = result.scalars().first()
    
    if not stage:
        raise HTTPException(status_code=400, detail="No stage defined for this edition")
    
    # 3. Basic logic: match all vs all (1 round)
    # In a real engine this would be more complex
    teams = [p.equipo_id for p in participants]
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            new_match = PartidoModel(
                edicion_id=edicion_id,
                etapa_id=stage.etapa_id,
                local_equipo_id=teams[i],
                visita_equipo_id=teams[j],
                estado_id=25 # PENDIENTE
            )
            db.add(new_match)
    
    await db.commit()
    return {"status": "success", "message": f"Fixture generated for {len(participants)} teams"}
