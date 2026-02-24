import asyncio
from sqlalchemy import text
from app.core.db import AsyncSessionLocal

async def inspect_data():
    async with AsyncSessionLocal() as session:
        print("Checking futsim.competencia:")
        result = await session.execute(text("SELECT competencia_id, nombre, mundo_id, tipo_id FROM futsim.competencia"))
        rows = result.all()
        if not rows:
            print("No records found in futsim.competencia")
        for row in rows:
            print(f"ID: {row.competencia_id}, Name: {row.nombre}, World: {row.mundo_id}, Type: {row.tipo_id}")

if __name__ == "__main__":
    asyncio.run(inspect_data())
