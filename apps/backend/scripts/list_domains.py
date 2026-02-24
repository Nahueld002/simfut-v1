import asyncio
import asyncpg
import os

async def run():
    try:
        conn = await asyncpg.connect(os.environ["DATABASE_URL"])
        rows = await conn.fetch('SELECT dominio_id, codigo FROM futsim.cat_dominio')
        for r in rows:
            print(f"{r['dominio_id']}: {r['codigo']}")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
