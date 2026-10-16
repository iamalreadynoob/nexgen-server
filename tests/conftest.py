"""Shared fixtures for the whole test suite."""

from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app
from app.schemas.actuator import ActuatorOut

TEST_API_KEY = "test-api-key"
FIXED_NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


@pytest.fixture
def settings() -> Settings:
    """Settings isolated from the developer's `.env` and environment."""
    return Settings(
        _env_file=None,
        api_key=TEST_API_KEY,
        environment="test",
    )


@pytest.fixture
def app(settings: Settings) -> Iterator[FastAPI]:
    """A fresh app per test, so dependency overrides never leak between tests."""
    application = create_app()
    application.dependency_overrides[get_settings] = lambda: settings
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """An authenticated client.

    It is not used as a context manager on purpose: the lifespan (which opens
    the Mongo client and sets up file logging) never runs in unit tests.
    """
    return TestClient(app, headers={"X-API-Key": TEST_API_KEY})


@pytest.fixture
def anon_client(app: FastAPI) -> TestClient:
    """A client that sends no API key."""
    return TestClient(app)


@pytest.fixture
def actuator_factory() -> Callable[..., ActuatorOut]:
    """Build a valid `ActuatorOut`; keyword arguments override single fields."""

    def _make(**overrides: Any) -> ActuatorOut:
        data = {
            "_id": "65f0c0ffee0000000000abcd",
            "name": "hamming",
            "version": "1.0.0",
            "actuator_type": "coding",
            "requirements": ["numpy"],
            "method": "def encode(bits):\n    return bits\n",
            "method_args": {"bits": {"type": "list[int]"}},
            "latest": True,
            "created_at": FIXED_NOW,
            "updated_at": FIXED_NOW,
            **overrides,
        }
        return ActuatorOut.model_validate(data)

    return _make
