from fastapi import APIRouter

from app.api.endpoints import login, models, versions

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(versions.router, prefix="/models/version", tags=["versions"])
