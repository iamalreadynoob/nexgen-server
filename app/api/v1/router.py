"""It handles the API routers."""

from fastapi import APIRouter, Depends

from app.api.v1.endpoints import actuators, health
from app.core.security import verify_api_key

api_router = APIRouter()

# Public routes
api_router.include_router(health.router)

# Protected routes: auth applied once, to everything included here.
protected = APIRouter(dependencies=[Depends(verify_api_key)])
protected.include_router(actuators.router)
api_router.include_router(protected)
