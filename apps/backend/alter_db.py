import asyncio
from sqlalchemy import text
from app.core.db import AsyncSessionLocal

async def alter_db():
    async with AsyncSessionLocal() as s:
        print('Testing DB altering...')
        await s.execute(text('ALTER TABLE futsim.competencia ADD COLUMN IF NOT EXISTS ciudad_id INT REFERENCES futsim.ciudad(ciudad_id);'))
        await s.commit()
        print('Added ciudad_id successfully')

asyncio.run(alter_db())
