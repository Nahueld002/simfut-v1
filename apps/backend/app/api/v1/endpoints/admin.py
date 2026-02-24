from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.seeding import SeedingService
from app.services.data_transfer import DataTransferService
from pydantic import BaseModel
import io
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter()

class SeedResponse(BaseModel):
    message: str

@router.post("/reset", response_model=SeedResponse)
async def reset_database(db: AsyncSession = Depends(get_db)):
    """Wipes all data from tables."""
    try:
        service = DataTransferService(db)
        logs = await service.reset_database()
        return {"message": "\n".join(logs)}
    except Exception as e:
        logger.error(f"DATABASE RESET ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset failed: {str(e)}"
        )

@router.post("/seed/world", response_model=SeedResponse)
async def seed_world(db: AsyncSession = Depends(get_db)):
    service = SeedingService(db)
    msg = await service.seed_world()
    return {"message": msg}

@router.post("/seed/geo", response_model=SeedResponse)
async def seed_geo(db: AsyncSession = Depends(get_db)):
    service = SeedingService(db)
    m1 = await service.seed_confederations()
    m2 = await service.seed_countries()
    m3 = await service.seed_paraguay_geo()
    return {"message": f"{m1} | {m2} | {m3}"}

@router.post("/seed/teams", response_model=SeedResponse)
async def seed_teams(db: AsyncSession = Depends(get_db)):
    service = SeedingService(db)
    msg = await service.seed_teams()
    return {"message": msg}

@router.post("/seed/tournaments", response_model=SeedResponse)
async def seed_tournaments(db: AsyncSession = Depends(get_db)):
    service = SeedingService(db)
    msg = await service.seed_tournaments()
    return {"message": msg}

@router.post("/seed/all", response_model=SeedResponse)
async def seed_all(db: AsyncSession = Depends(get_db)):
    service = SeedingService(db)
    await service.reset_db()
    await service.seed_world()
    await service.seed_confederations()
    await service.seed_countries()
    await service.seed_paraguay_geo()
    await service.seed_teams()
    msg = await service.seed_tournaments()
    return {"message": f"Full seed complete. {msg}"}

# --- Import / Export ---
@router.get("/export")
async def export_db(db: AsyncSession = Depends(get_db)):
    """Exports the database to an Excel file (Native Download)."""
    service = DataTransferService(db)
    
    try:
        print("EXPORT: starting generation...")
        file_bytes, logs = await service.export_to_excel()
        print(f"EXPORT: generated {len(file_bytes)} bytes")
        
        # Log logs to stdout
        for l in logs:
            print(l)
        
        return Response(
            content=file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=futsim_dump.xlsx; filename*=UTF-8''futsim_dump.xlsx",
                "Content-Length": str(len(file_bytes)),
                "Cache-Control": "no-store",
                "Pragma": "no-cache",
            }
        )
    except Exception as e:
        print(f"EXPORT ERROR: {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import", response_model=SeedResponse)
async def import_db(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Imports data from an Excel file (Massive Dump)."""
    try:
        logger.info(f"IMPORT: Starting import of file {file.filename}")
        service = DataTransferService(db)
        content = await file.read()
        logs = await service.import_from_excel(content)
        
        # Join logs into a single message or return as structure
        # The BaseModel expects "message" as str
        logger.info("IMPORT: Completed successfully")
        return {"message": "\n".join(logs)}
    except Exception as e:
        logger.error(f"IMPORT ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Try to provide a more specific error message from SQLAlchemy/asyncpg
        error_detail = str(e)
        
        # Extract underlying error if possible
        if hasattr(e, 'orig') and hasattr(e.orig, '__dict__'):
            # asyncpg errors have specific attributes like 'message', 'detail', 'where', 'table_name', 'column_name'
            orig = e.orig
            if hasattr(orig, 'message'):
                error_detail = f"{orig.message}"
            if hasattr(orig, 'detail') and orig.detail:
                error_detail += f" | Detail: {orig.detail}"
            if hasattr(orig, 'table_name') and orig.table_name:
                error_detail += f" | Table: {orig.table_name}"
            if hasattr(orig, 'column_name') and orig.column_name:
                error_detail += f" | Column: {orig.column_name}"
        
        if "UniqueViolationError" in error_detail:
            error_detail = "Database Integrity Error: Duplicate keys detected. " + error_detail
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{error_detail}"
        )
