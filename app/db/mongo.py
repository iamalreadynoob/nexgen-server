"""Initializes the mongo database."""

import logging

from fastapi import Request
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import Settings

logger = logging.getLogger(__name__)


def create_client(settings: Settings) -> AsyncMongoClient:
    """One client per process. It owns a connection pool shared by all requests."""
    return AsyncMongoClient(
        settings.mongodb_uri,
        maxPoolSize=settings.mongodb_max_pool_size,
        minPoolSize=settings.mongodb_min_pool_size,
        serverSelectionTimeoutMS=5000,
        tz_aware=True,
    )


def get_database(request: Request) -> AsyncDatabase:
    """FastAPI dependency: returns the DB bound in the lifespan."""
    return request.app.state.db
