import asyncio
from sqlalchemy import text
from app.core.db import AsyncSessionLocal

async def check_edition():
    async with AsyncSessionLocal() as s:
        r = await s.execute(text('SELECT * FROM futsim.competencia_edicion WHERE edicion_id = 8'))
        print(r.mappings().first())

asyncio.run(check_edition())
