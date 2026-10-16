"""Dependency wiring: DB -> repository -> service."""

from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.db.mongo import get_database
from app.repositories.actuator_repository import ActuatorRepository
from app.repositories.data_repository import DataRepository
from app.services.actuator_service import ActuatorService
from app.services.data_service import DataService


def get_actuator_service(
    db: AsyncDatabase = Depends(get_database),
) -> ActuatorService:
    """# Get Actuator Service."""
    return ActuatorService(ActuatorRepository(db))


def get_data_service(
    db: AsyncDatabase = Depends(get_database),
) -> DataService:
    """# Get Data Service."""
    return DataService(
        repo=DataRepository(db),
        actuator_repo=ActuatorRepository(db),
    )
