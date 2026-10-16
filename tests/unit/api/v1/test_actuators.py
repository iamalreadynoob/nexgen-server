"""Unit tests for the actuator endpoints.

The service layer is replaced by an autospec'd mock, so these tests cover
only the HTTP contract: routing, status codes, request validation, parameter
forwarding, response serialization, error mapping and auth.
"""

from collections.abc import Callable
from typing import Any
from unittest.mock import create_autospec

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.deps import get_actuator_service
from app.core.config import Settings
from app.core.exceptions import (
    AlreadyExistsError,
    LatestDeletionError,
    NotFoundError,
)
from app.schemas.actuator import ActuatorCreate, ActuatorList, ActuatorOut
from app.services.actuator_service import ActuatorService

BASE_URL = "/api/v1/actuators"
ACTUATOR_ID = "65f0c0ffee0000000000abcd"

ActuatorFactory = Callable[..., ActuatorOut]


@pytest.fixture
def actuator_service(app: FastAPI) -> ActuatorService:
    """Mocked service; its async methods become `AsyncMock`s via autospec."""
    service = create_autospec(ActuatorService, instance=True)
    app.dependency_overrides[get_actuator_service] = lambda: service
    return service


@pytest.fixture
def create_payload() -> dict[str, Any]:
    """A valid request body for `POST /actuators`."""
    return {
        "name": "hamming",
        "version": "1.0.0",
        "actuator_type": "coding",
        "requirements": ["numpy"],
        "method": "def encode(bits):\n    return bits\n",
    }


def _json(actuator: ActuatorOut) -> dict[str, Any]:
    """The JSON FastAPI renders for a model (`response_model_by_alias=True`)."""
    return actuator.model_dump(mode="json", by_alias=True)


class TestListActuators:
    def test_returns_list(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
    ):
        actuator = actuator_factory()
        actuator_service.get_actuators.return_value = ActuatorList(
            total=1,
            actuators=[actuator],
        )

        response = client.get(BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"total": 1, "actuators": [_json(actuator)]}

    def test_forwards_default_query_params(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.get_actuators.return_value = ActuatorList(
            total=0,
            actuators=[],
        )

        client.get(BASE_URL)

        actuator_service.get_actuators.assert_awaited_once_with(
            page=1,
            limit=10,
            ascending=False,
            latest=None,
        )

    def test_forwards_custom_query_params(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.get_actuators.return_value = ActuatorList(
            total=0,
            actuators=[],
        )

        client.get(
            BASE_URL,
            params={"page": 3, "limit": 25, "ascending": "true", "latest": "false"},
        )

        actuator_service.get_actuators.assert_awaited_once_with(
            page=3,
            limit=25,
            ascending=True,
            latest=False,
        )

    @pytest.mark.parametrize(
        "params",
        [
            {"page": "abc"},
            {"limit": "ten"},
            {"ascending": "maybe"},
            {"latest": "maybe"},
        ],
    )
    def test_rejects_invalid_query_params(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        params: dict[str, str],
    ):
        response = client.get(BASE_URL, params=params)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        actuator_service.get_actuators.assert_not_awaited()


class TestGetActuator:
    def test_returns_actuator(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
    ):
        actuator = actuator_factory()
        actuator_service.get_actuator.return_value = actuator

        response = client.get(f"{BASE_URL}/{ACTUATOR_ID}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _json(actuator)
        actuator_service.get_actuator.assert_awaited_once_with(
            actuator_id=ACTUATOR_ID,
        )

    def test_not_found(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.get_actuator.side_effect = NotFoundError(
            resource="Actuator",
            identifier=ACTUATOR_ID,
        )

        response = client.get(f"{BASE_URL}/{ACTUATOR_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": f"Actuator '{ACTUATOR_ID}' not found",
        }


class TestGetLatestActuator:
    def test_returns_latest(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
    ):
        actuator = actuator_factory(name="hamming", latest=True)
        actuator_service.get_latest_actuator.return_value = actuator

        response = client.get(f"{BASE_URL}/hamming/latest")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _json(actuator)
        actuator_service.get_latest_actuator.assert_awaited_once_with(
            actuator_name="hamming",
        )

    def test_is_not_shadowed_by_get_by_id(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
    ):
        actuator_service.get_latest_actuator.return_value = actuator_factory()

        client.get(f"{BASE_URL}/hamming/latest")

        actuator_service.get_actuator.assert_not_awaited()

    def test_not_found(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.get_latest_actuator.side_effect = NotFoundError(
            resource="Actuator",
            identifier="unknown",
        )

        response = client.get(f"{BASE_URL}/unknown/latest")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Actuator 'unknown' not found"}


class TestCreateActuator:
    def test_creates_actuator(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
        create_payload: dict[str, Any],
    ):
        actuator = actuator_factory()
        actuator_service.create_actuator.return_value = actuator

        response = client.post(BASE_URL, json=create_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == _json(actuator)

    def test_forwards_parsed_payload(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
        create_payload: dict[str, Any],
    ):
        actuator_service.create_actuator.return_value = actuator_factory()

        client.post(BASE_URL, json={**create_payload, "set_latest": True})

        actuator_service.create_actuator.assert_awaited_once_with(
            payload=ActuatorCreate(**create_payload, set_latest=True),
        )

    def test_set_latest_defaults_to_false(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
        create_payload: dict[str, Any],
    ):
        actuator_service.create_actuator.return_value = actuator_factory()

        client.post(BASE_URL, json=create_payload)

        payload = actuator_service.create_actuator.await_args.kwargs["payload"]
        assert payload.set_latest is False

    def test_already_exists(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        create_payload: dict[str, Any],
    ):
        actuator_service.create_actuator.side_effect = AlreadyExistsError(
            resource="Actuator",
            identifier="hamming (1.0.0)",
        )

        response = client.post(BASE_URL, json=create_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "Actuator 'hamming (1.0.0)' already exists",
        }

    @pytest.mark.parametrize(
        "missing_field",
        ["name", "version", "actuator_type", "requirements", "method"],
    )
    def test_rejects_missing_required_field(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        create_payload: dict[str, Any],
        missing_field: str,
    ):
        del create_payload[missing_field]

        response = client.post(BASE_URL, json=create_payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0]["loc"] == ["body", missing_field]
        actuator_service.create_actuator.assert_not_awaited()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("name", ""),
            ("name", "x" * 65),
            ("version", ""),
            ("version", "x" * 129),
            ("actuator_type", "encoding"),
            ("requirements", "numpy"),
            ("method_args", {"bits": "list[int]"}),
            ("set_latest", "sometimes"),
        ],
    )
    def test_rejects_invalid_field(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        create_payload: dict[str, Any],
        field: str,
        value: Any,
    ):
        response = client.post(BASE_URL, json={**create_payload, field: value})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0]["loc"][:2] == ["body", field]
        actuator_service.create_actuator.assert_not_awaited()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("name", "x"),
            ("name", "x" * 64),
            ("version", "x" * 128),
            ("actuator_type", "decoding"),
            ("requirements", []),
        ],
    )
    def test_accepts_boundary_values(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
        create_payload: dict[str, Any],
        field: str,
        value: Any,
    ):
        actuator_service.create_actuator.return_value = actuator_factory()

        response = client.post(BASE_URL, json={**create_payload, field: value})

        assert response.status_code == status.HTTP_201_CREATED

    def test_rejects_non_json_body(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        response = client.post(
            BASE_URL,
            content="not json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        actuator_service.create_actuator.assert_not_awaited()


class TestSetLatestActuator:
    def test_sets_latest(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
        actuator_factory: ActuatorFactory,
    ):
        actuator = actuator_factory(latest=True)
        actuator_service.set_latest_actuator.return_value = actuator

        response = client.put(f"{BASE_URL}/{ACTUATOR_ID}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _json(actuator)
        actuator_service.set_latest_actuator.assert_awaited_once_with(
            actuator_id=ACTUATOR_ID,
        )

    def test_not_found(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.set_latest_actuator.side_effect = NotFoundError(
            resource="Actuator",
            identifier=ACTUATOR_ID,
        )

        response = client.put(f"{BASE_URL}/{ACTUATOR_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_already_latest(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.set_latest_actuator.side_effect = AlreadyExistsError(
            resource="Actuator",
            identifier=f"{ACTUATOR_ID} (latest: True)",
        )

        response = client.put(f"{BASE_URL}/{ACTUATOR_ID}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteActuator:
    def test_deletes_actuator(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.delete_actuator.return_value = None

        response = client.delete(f"{BASE_URL}/{ACTUATOR_ID}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        actuator_service.delete_actuator.assert_awaited_once_with(
            actuator_id=ACTUATOR_ID,
        )

    def test_not_found(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.delete_actuator.side_effect = NotFoundError(
            resource="Actuator",
            identifier=ACTUATOR_ID,
        )

        response = client.delete(f"{BASE_URL}/{ACTUATOR_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_rejects_deleting_latest(
        self,
        client: TestClient,
        actuator_service: ActuatorService,
    ):
        actuator_service.delete_actuator.side_effect = LatestDeletionError(
            resource="Actuator",
            identifier=ACTUATOR_ID,
        )

        response = client.delete(f"{BASE_URL}/{ACTUATOR_ID}")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": (
                f"Actuator '{ACTUATOR_ID}' is the latest one and cannot be deleted"
            ),
        }


ALL_ROUTES = [
    ("GET", BASE_URL),
    ("GET", f"{BASE_URL}/{ACTUATOR_ID}"),
    ("GET", f"{BASE_URL}/hamming/latest"),
    ("POST", BASE_URL),
    ("PUT", f"{BASE_URL}/{ACTUATOR_ID}"),
    ("DELETE", f"{BASE_URL}/{ACTUATOR_ID}"),
]


@pytest.fixture
def stub_service(actuator_service: ActuatorService) -> ActuatorService:
    """Every service method fails fast, so any authorized request ends cleanly."""
    for name in (
        "get_actuators",
        "get_actuator",
        "get_latest_actuator",
        "create_actuator",
        "set_latest_actuator",
        "delete_actuator",
    ):
        getattr(actuator_service, name).side_effect = NotFoundError(
            resource="Actuator",
            identifier="stub",
        )
    return actuator_service


@pytest.mark.parametrize(("method", "url"), ALL_ROUTES)
class TestAuth:
    def test_rejects_missing_key(
        self,
        anon_client: TestClient,
        actuator_service: ActuatorService,
        method: str,
        url: str,
    ):
        response = anon_client.request(method, url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.headers["WWW-Authenticate"] == "ApiKey"
        assert not actuator_service.method_calls

    def test_rejects_wrong_key(
        self,
        anon_client: TestClient,
        actuator_service: ActuatorService,
        method: str,
        url: str,
    ):
        response = anon_client.request(
            method,
            url,
            headers={"X-API-Key": "wrong-key"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not actuator_service.method_calls

    @pytest.mark.usefixtures("stub_service")
    def test_accepts_any_configured_key(
        self,
        anon_client: TestClient,
        settings: Settings,
        method: str,
        url: str,
    ):
        settings.api_key = "first-key, second-key"

        response = anon_client.request(
            method,
            url,
            headers={"X-API-Key": "second-key"},
        )

        assert response.status_code != status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("stub_service")
    def test_open_when_auth_disabled(
        self,
        anon_client: TestClient,
        settings: Settings,
        method: str,
        url: str,
    ):
        settings.api_key = None

        response = anon_client.request(method, url)

        assert response.status_code != status.HTTP_401_UNAUTHORIZED
