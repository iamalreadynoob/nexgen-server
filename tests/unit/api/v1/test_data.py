"""Unit tests for the data endpoints.

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

from app.api.deps import get_data_service
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.schemas.data import (
    DataCreate,
    DataList,
    DataMetadataOut,
    DataOut,
    DataUpdate,
)
from app.services.data_service import DataService

BASE_URL = "/api/v1/data"
DATA_ID = "65f0c0ffee000000000da7a0"
ACTUATOR_ID = "65f0c0ffee0000000000abcd"

DataFactory = Callable[..., DataOut]


@pytest.fixture
def data_service(app: FastAPI) -> DataService:
    """Mocked service; its async methods become `AsyncMock`s via autospec."""
    service = create_autospec(DataService, instance=True)
    app.dependency_overrides[get_data_service] = lambda: service
    return service


@pytest.fixture
def create_payload() -> dict[str, Any]:
    """A valid request body for `POST /data`."""
    return {
        "actuator_id": ACTUATOR_ID,
        "metadata": {"bits": [1, 0, 1, 1]},
        "linked_resource": "input-001",
        "specs": {"rate": 0.5},
    }


def _json(data: DataOut) -> dict[str, Any]:
    """The JSON FastAPI renders for a model (`response_model_by_alias=True`)."""
    return data.model_dump(mode="json", by_alias=True)


class TestListData:
    def test_returns_list(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
    ):
        data = data_factory()
        data_service.get_data_list.return_value = DataList(total=1, data=[data])

        response = client.get(BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"total": 1, "data": [_json(data)]}

    def test_returns_empty_list(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        data_service.get_data_list.return_value = DataList(total=0, data=[])

        response = client.get(BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"total": 0, "data": []}

    def test_forwards_default_query_params(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        data_service.get_data_list.return_value = DataList(total=0, data=[])

        client.get(BASE_URL)

        data_service.get_data_list.assert_awaited_once_with(
            page=1,
            limit=10,
            ascending=False,
            actuator_id=None,
        )

    def test_forwards_custom_query_params(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        data_service.get_data_list.return_value = DataList(total=0, data=[])

        client.get(
            BASE_URL,
            params={
                "page": 3,
                "limit": 25,
                "ascending": "true",
                "actuator_id": ACTUATOR_ID,
            },
        )

        data_service.get_data_list.assert_awaited_once_with(
            page=3,
            limit=25,
            ascending=True,
            actuator_id=ACTUATOR_ID,
        )

    @pytest.mark.parametrize(
        "params",
        [
            {"page": "abc"},
            {"limit": "ten"},
            {"ascending": "maybe"},
        ],
    )
    def test_rejects_invalid_query_params(
        self,
        client: TestClient,
        data_service: DataService,
        params: dict[str, str],
    ):
        response = client.get(BASE_URL, params=params)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data_service.get_data_list.assert_not_awaited()


class TestGetData:
    def test_returns_data(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
    ):
        data = data_factory()
        data_service.get_data.return_value = data

        response = client.get(f"{BASE_URL}/{DATA_ID}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _json(data)
        data_service.get_data.assert_awaited_once_with(
            data_id=DATA_ID,
            metadata_only=False,
        )

    def test_forwards_metadata_only(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
    ):
        data_service.get_data.return_value = data_factory()

        client.get(f"{BASE_URL}/{DATA_ID}", params={"metadata_only": "true"})

        data_service.get_data.assert_awaited_once_with(
            data_id=DATA_ID,
            metadata_only=True,
        )

    def test_returns_metadata_only(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        data_service.get_data.return_value = DataMetadataOut(
            id=DATA_ID,
            actuator_id=ACTUATOR_ID,
            metadata={"bits": [1, 0, 1, 1]},
        )

        response = client.get(
            f"{BASE_URL}/{DATA_ID}",
            params={"metadata_only": "true"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": DATA_ID,
            "actuator_id": ACTUATOR_ID,
            "metadata": {"bits": [1, 0, 1, 1]},
        }

    def test_full_response_keeps_all_fields(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
    ):
        data_service.get_data.return_value = data_factory()

        response = client.get(f"{BASE_URL}/{DATA_ID}")

        assert set(response.json()) == set(DataOut.model_fields)

    def test_rejects_invalid_metadata_only(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        response = client.get(
            f"{BASE_URL}/{DATA_ID}",
            params={"metadata_only": "maybe"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data_service.get_data.assert_not_awaited()

    def test_not_found(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        data_service.get_data.side_effect = NotFoundError(
            resource="Data",
            identifier=DATA_ID,
        )

        response = client.get(f"{BASE_URL}/{DATA_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": f"Data '{DATA_ID}' not found"}


class TestCreateData:
    def test_creates_data(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
        create_payload: dict[str, Any],
    ):
        data = data_factory()
        data_service.create_data.return_value = data

        response = client.post(BASE_URL, json=create_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == _json(data)

    def test_forwards_parsed_payload(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
        create_payload: dict[str, Any],
    ):
        data_service.create_data.return_value = data_factory()

        client.post(BASE_URL, json=create_payload)

        data_service.create_data.assert_awaited_once_with(
            payload=DataCreate(**create_payload),
        )

    def test_actuator_not_latest(
        self,
        client: TestClient,
        data_service: DataService,
        create_payload: dict[str, Any],
    ):
        data_service.create_data.side_effect = NotFoundError(
            resource="Actuator",
            identifier=ACTUATOR_ID,
        )

        response = client.post(BASE_URL, json=create_payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": f"Actuator '{ACTUATOR_ID}' not found"}

    @pytest.mark.parametrize(
        "metadata",
        [
            {"bits": [1, 0, 1]},
            [1, 0, 1],
            "encoded-text",
            42,
            3.5,
            True,
        ],
    )
    def test_accepts_any_json_metadata(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
        create_payload: dict[str, Any],
        metadata: Any,
    ):
        data_service.create_data.return_value = data_factory(metadata=metadata)

        response = client.post(BASE_URL, json={**create_payload, "metadata": metadata})

        assert response.status_code == status.HTTP_201_CREATED
        payload = data_service.create_data.await_args.kwargs["payload"]
        assert payload.metadata == metadata

    @pytest.mark.parametrize("field", ["linked_resource", "specs"])
    def test_accepts_null_optional_field(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
        create_payload: dict[str, Any],
        field: str,
    ):
        data_service.create_data.return_value = data_factory(**{field: None})

        response = client.post(BASE_URL, json={**create_payload, field: None})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()[field] is None

    @pytest.mark.parametrize(
        "missing_field",
        ["actuator_id", "metadata", "linked_resource", "specs"],
    )
    def test_rejects_missing_required_field(
        self,
        client: TestClient,
        data_service: DataService,
        create_payload: dict[str, Any],
        missing_field: str,
    ):
        del create_payload[missing_field]

        response = client.post(BASE_URL, json=create_payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0]["loc"] == ["body", missing_field]
        data_service.create_data.assert_not_awaited()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("actuator_id", None),
            ("actuator_id", 123),
            ("linked_resource", 123),
            ("specs", "fast"),
            ("specs", [1, 2]),
        ],
    )
    def test_rejects_invalid_field(
        self,
        client: TestClient,
        data_service: DataService,
        create_payload: dict[str, Any],
        field: str,
        value: Any,
    ):
        response = client.post(BASE_URL, json={**create_payload, field: value})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0]["loc"][:2] == ["body", field]
        data_service.create_data.assert_not_awaited()

    def test_rejects_non_json_body(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        response = client.post(
            BASE_URL,
            content="not json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data_service.create_data.assert_not_awaited()


class TestUpdateData:
    def test_updates_data(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
    ):
        data = data_factory(linked_resource="input-002", specs={"rate": 0.75})
        data_service.update_data.return_value = data

        response = client.put(
            f"{BASE_URL}/{DATA_ID}",
            json={"linked_resource": "input-002", "specs": {"rate": 0.75}},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _json(data)
        data_service.update_data.assert_awaited_once_with(
            data_id=DATA_ID,
            payload=DataUpdate(linked_resource="input-002", specs={"rate": 0.75}),
        )

    @pytest.mark.parametrize(
        "body",
        [
            {},
            {"linked_resource": "input-002"},
            {"specs": {"rate": 0.75}},
            {"linked_resource": None, "specs": None},
        ],
    )
    def test_accepts_partial_body(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
        body: dict[str, Any],
    ):
        data_service.update_data.return_value = data_factory()

        response = client.put(f"{BASE_URL}/{DATA_ID}", json=body)

        assert response.status_code == status.HTTP_200_OK
        data_service.update_data.assert_awaited_once_with(
            data_id=DATA_ID,
            payload=DataUpdate(**body),
        )

    def test_ignores_read_only_fields(
        self,
        client: TestClient,
        data_service: DataService,
        data_factory: DataFactory,
    ):
        data_service.update_data.return_value = data_factory()

        client.put(
            f"{BASE_URL}/{DATA_ID}",
            json={"actuator_id": "other", "metadata": "other", "specs": {}},
        )

        data_service.update_data.assert_awaited_once_with(
            data_id=DATA_ID,
            payload=DataUpdate(specs={}),
        )

    def test_not_found(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        data_service.update_data.side_effect = NotFoundError(
            resource="Data",
            identifier=DATA_ID,
        )

        response = client.put(f"{BASE_URL}/{DATA_ID}", json={})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": f"Data '{DATA_ID}' not found"}

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("linked_resource", 123),
            ("specs", "fast"),
            ("specs", [1, 2]),
        ],
    )
    def test_rejects_invalid_field(
        self,
        client: TestClient,
        data_service: DataService,
        field: str,
        value: Any,
    ):
        response = client.put(f"{BASE_URL}/{DATA_ID}", json={field: value})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0]["loc"][:2] == ["body", field]
        data_service.update_data.assert_not_awaited()

    def test_rejects_missing_body(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        response = client.put(f"{BASE_URL}/{DATA_ID}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data_service.update_data.assert_not_awaited()


class TestDeleteData:
    def test_deletes_data(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        data_service.delete_data.return_value = None

        response = client.delete(f"{BASE_URL}/{DATA_ID}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        data_service.delete_data.assert_awaited_once_with(
            data_id=DATA_ID,
        )

    def test_not_found(
        self,
        client: TestClient,
        data_service: DataService,
    ):
        data_service.delete_data.side_effect = NotFoundError(
            resource="Data",
            identifier=DATA_ID,
        )

        response = client.delete(f"{BASE_URL}/{DATA_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": f"Data '{DATA_ID}' not found"}


ALL_ROUTES = [
    ("GET", BASE_URL),
    ("GET", f"{BASE_URL}/{DATA_ID}"),
    ("POST", BASE_URL),
    ("PUT", f"{BASE_URL}/{DATA_ID}"),
    ("DELETE", f"{BASE_URL}/{DATA_ID}"),
]


@pytest.fixture
def stub_service(data_service: DataService) -> DataService:
    """Every service method fails fast, so any authorized request ends cleanly."""
    for name in (
        "get_data_list",
        "get_data",
        "create_data",
        "update_data",
        "delete_data",
    ):
        getattr(data_service, name).side_effect = NotFoundError(
            resource="Data",
            identifier="stub",
        )
    return data_service


@pytest.mark.parametrize(("method", "url"), ALL_ROUTES)
class TestAuth:
    def test_rejects_missing_key(
        self,
        anon_client: TestClient,
        data_service: DataService,
        method: str,
        url: str,
    ):
        response = anon_client.request(method, url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.headers["WWW-Authenticate"] == "ApiKey"
        assert not data_service.method_calls

    def test_rejects_wrong_key(
        self,
        anon_client: TestClient,
        data_service: DataService,
        method: str,
        url: str,
    ):
        response = anon_client.request(
            method,
            url,
            headers={"X-API-Key": "wrong-key"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not data_service.method_calls

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
