from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.core import db
from app.models.team import Rivalidad
from pydantic import BaseModel, Field

router = APIRouter()

class RivalidadCreate(BaseModel):
    equipo_a_id: int
    equipo_b_id: int
    nombre: str = None
    intensidad: int = Field(50, ge=0, le=100)

class RivalidadSchema(RivalidadCreate):
    rivalidad_id: int

@router.post("/", response_model=RivalidadSchema)
async def create_rivalidad(
    rivalidad: RivalidadCreate,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Create a rivalry. Automatically sorts IDs so A < B.
    """
    # 1. Sort IDs
    id_1, id_2 = sorted([rivalidad.equipo_a_id, rivalidad.equipo_b_id])
    
    if id_1 == id_2:
        raise HTTPException(status_code=400, detail="Cannot create rivalry with self")

    # 2. Check existence
    stmt = select(Rivalidad).where(
        and_(Rivalidad.equipo_a_id == id_1, Rivalidad.equipo_b_id == id_2)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
         raise HTTPException(status_code=400, detail="Rivalry already exists")

    # 3. Create
    db_obj = Rivalidad(
        equipo_a_id=id_1,
        equipo_b_id=id_2,
        nombre=rivalidad.nombre,
        intensidad=rivalidad.intensidad
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.get("/team/{equipo_id}", response_model=list[RivalidadSchema])
async def get_team_rivalries(
    equipo_id: int,
    db: AsyncSession = Depends(db.get_db),
):
    """
    Get all rivalries for a team (whether A or B).
    """
    stmt = select(Rivalidad).where(
        or_(Rivalidad.equipo_a_id == equipo_id, Rivalidad.equipo_b_id == equipo_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.delete("/{rivalidad_id}")
async def delete_rivalidad(
    rivalidad_id: int,
    db: AsyncSession = Depends(db.get_db),
):
    stmt = select(Rivalidad).where(Rivalidad.rivalidad_id == rivalidad_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Rivalry not found")
        
    await db.delete(obj)
    await db.commit()
    return {"message": "Deleted"}
