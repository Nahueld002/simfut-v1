from typing import Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_all(db: AsyncSession, model: Any, skip: int = 0, limit: int = 100) -> List[Any]:
    result = await db.execute(select(model).offset(skip).limit(limit))
    return result.scalars().all()

async def create(db: AsyncSession, model: Any, obj_in: dict) -> Any:
    db_obj = model(**obj_in)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
