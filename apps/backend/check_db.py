import asyncio
from sqlalchemy import text
from app.core.db import get_db, AsyncSessionLocal

async def check_counts():
    async with AsyncSessionLocal() as session:
        tables = [
            "futsim.competencia",
            "futsim.competencia_edicion",
            "futsim.equipo",
            "futsim.pais",
            "futsim.cat_parametro"
        ]
        for table in tables:
            try:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"{table}: {count} records")
            except Exception as e:
                print(f"Error checking {table}: {e}")

if __name__ == "__main__":
    asyncio.run(check_counts())
