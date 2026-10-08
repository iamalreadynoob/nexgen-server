"""Dependency wiring: DB -> repository -> service."""

from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.db.mongo import get_database
from app.repositories.actuator_repository import ActuatorRepository
from app.services.actuator_service import ActuatorService


def get_actuator_service(
    db: AsyncDatabase = Depends(get_database),
) -> ActuatorService:
    """# Get Actuator Service."""
    return ActuatorService(ActuatorRepository(db))
