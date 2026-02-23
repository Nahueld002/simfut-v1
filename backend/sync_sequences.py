import asyncio
from sqlalchemy import text
from app.core.db import AsyncSessionLocal

async def sync_sequences():
    print("Syncing sequences for futsim schema...")
    # Table and its PK column name
    tables = {
        "equipo": "equipo_id",
        "pais": "pais_id",
        "region": "region_id",
        "ciudad": "ciudad_id",
        "asociacion": "asociacion_id",
        "estadio": "estadio_id",
        "competencia": "competencia_id",
        "competencia_edicion": "edicion_id",
        "participante": "participante_id",
        "rivalidad": "rivalidad_id"
    }
    
    async with AsyncSessionLocal() as db:
        for table, id_col in tables.items():
            try:
                # Get max ID
                res = await db.execute(text(f"SELECT MAX({id_col}) FROM futsim.{table}"))
                max_id = res.scalar()
                
                if max_id:
                    seq_name = f"futsim.{table}_{id_col}_seq"
                    # Check if sequence exists
                    await db.execute(text(f"SELECT setval('{seq_name}', {max_id})"))
                    print(f"Synced {seq_name} to {max_id}")
                await db.commit() # Commit each one
            except Exception as e:
                await db.rollback() # Rollback on error to keep transaction clean
                print(f"Skipping {table}: {e}")
        
    print("Done.")

if __name__ == "__main__":
    asyncio.run(sync_sequences())
