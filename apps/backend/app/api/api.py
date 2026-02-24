from fastapi import APIRouter
from app.api.v1.endpoints import worlds, teams, admin, rivalries, stadiums, lookups, media, competitions

api_router = APIRouter()
api_router.include_router(worlds.router, prefix="/worlds", tags=["worlds"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(rivalries.router, prefix="/rivalries", tags=["rivalries"])
api_router.include_router(stadiums.router, prefix="/stadiums", tags=["stadiums"])
api_router.include_router(lookups.router, prefix="/lookups", tags=["lookups"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
