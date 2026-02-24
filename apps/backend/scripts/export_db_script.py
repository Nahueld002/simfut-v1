#!/usr/bin/env python3
import asyncio
import sys
import os

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import AsyncSessionLocal
from app.services.data_transfer import DataTransferService

async def main():
    output_file = "dump_futsim.xlsx"
    print("Starting export...")
    
    async with AsyncSessionLocal() as session:
        service = DataTransferService(session)
        data, logs = await service.export_to_excel()
        
        for l in logs:
            print(l)
        
        with open(output_file, "wb") as f:
            f.write(data)
            
    print(f"Export complete: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
