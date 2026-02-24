from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core import db
from app.models.common import MediaAsset
from app.core.config import settings
import uuid
import shutil
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("/home/nahuel/estudios/sgdba/TP_FINAL_NMDM/backend/uploads")

import hashlib
from PIL import Image

@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(None),
    db: AsyncSession = Depends(db.get_db)
):
    """
    Upload a file (PNG/JPG) and return its Media ID.
    Populates metadata: width, height, checksum, size.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate UUID
    media_id = uuid.uuid4()
    extension = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{media_id}.{extension}"
    file_path = UPLOAD_DIR / filename
    
    # Save file and calculate checksum
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "wb") as buffer:
            while chunk := file.file.read(4096):
                buffer.write(chunk)
                hash_md5.update(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
        
    checksum = hash_md5.hexdigest()
    
    # Get Image Dimensions
    width, height = None, None
    try:
        with Image.open(file_path) as img:
            width, height = img.size
    except Exception as e:
        print(f"Warning: Could not get image dimensions: {e}")
        
    # Create DB Record
    url = f"/uploads/{filename}"
    file_size = file_path.stat().st_size
    
    meta_data = {}
    if category:
        meta_data["category"] = category

    media_asset = MediaAsset(
        media_id=media_id,
        url=url,
        mime_type=file.content_type,
        bytes=file_size,
        checksum=checksum,
        ancho=width,
        alto=height,
        meta=meta_data
    )
    
    db.add(media_asset)
    await db.commit()
    await db.refresh(media_asset)
    
    return {"media_id": str(media_asset.media_id), "url": media_asset.url}
