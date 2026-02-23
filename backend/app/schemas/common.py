from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class MediaAsset(BaseModel):
    media_id: UUID
    url: str
    mime_type: Optional[str] = None
    
    checksum: Optional[str] = None
    ancho: Optional[int] = None
    alto: Optional[int] = None
    meta: Optional[dict] = {}
    
    model_config = ConfigDict(from_attributes=True)
