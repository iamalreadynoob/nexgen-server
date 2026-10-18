"""Unit tests for the content endpoints.

The service layer is replaced by an autospec'd mock, so these tests cover
only the HTTP contract: routing, status codes, request validation, parameter
forwarding (including the JSON `specs` filter), response serialization,
error mapping and auth.
"""

from collections.abc import Callable
from typing import Any
from unittest.mock import create_autospec

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.deps import get_content_service
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.schemas.contents import (
    ContentCreate,
    ContentList,
    ContentOut,
    ContentSetSpecs,
)
from app.services.content_service import ContentService

BASE_URL = "/api/v1/contents"
CONTENT_ID = "65f0c0ffee00000000c0ffee"
SPECS_FORMAT_ERROR = {"detail": "specs must be a valid JSON object"}

ContentFactory = Callable[..., ContentOut]


@pytest.fixture
def content_service(app: FastAPI) -> ContentService:
    """Mocked service; its async methods become `AsyncMock`s via autospec."""
    service = create_autospec(ContentService, instance=True)
    app.dependency_overrides[get_content_service] = lambda: service
    return service


@pytest.fixture
def create_payload() -> dict[str, Any]:
    """A valid request body for `POST /contents`."""
    return {
        "identifier": "input-001",
        "specs": {"color": "red", "size": 5},
    }


def _json(content: ContentOut) -> dict[str, Any]:
    """The JSON FastAPI renders for a model (`response_model_by_alias=True`)."""
    return content.model_dump(mode="json", by_alias=True)


class TestListContents:
    def test_returns_list(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
    ):
        content = content_factory()
        content_service.get_contents.return_value = ContentList(
            total=1,
            data=[content],
        )

        response = client.get(BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"total": 1, "data": [_json(content)]}

    def test_returns_empty_list(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        content_service.get_contents.return_value = ContentList(total=0, data=[])

        response = client.get(BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"total": 0, "data": []}

    def test_forwards_default_query_params(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        content_service.get_contents.return_value = ContentList(total=0, data=[])

        client.get(BASE_URL)

        content_service.get_contents.assert_awaited_once_with(
            page=1,
            limit=10,
            ascending=False,
            specs=None,
        )

    def test_forwards_custom_query_params(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        content_service.get_contents.return_value = ContentList(total=0, data=[])

        client.get(
            BASE_URL,
            params={
                "page": 3,
                "limit": 25,
                "ascending": "true",
                "specs": '{"color": "red", "size": 5}',
            },
        )

        content_service.get_contents.assert_awaited_once_with(
            page=3,
            limit=25,
            ascending=True,
            specs={"color": "red", "size": 5},
        )

    @pytest.mark.parametrize(
        ("raw", "parsed"),
        [
            ("{}", {}),
            (
                '{"size": 5.5, "ok": true, "gone": null}',
                {"size": 5.5, "ok": True, "gone": None},
            ),
            (
                '{"meta": {"a": 1}, "tags": ["x", "y"]}',
                {"meta": {"a": 1}, "tags": ["x", "y"]},
            ),
            # An operator-looking key is passed on as plain data; the repository
            # compares it with `$eq`, so it is never run as a query operator.
            ('{"$where": "1"}', {"$where": "1"}),
        ],
    )
    def test_parses_specs_filter(
        self,
        client: TestClient,
        content_service: ContentService,
        raw: str,
        parsed: dict[str, Any],
    ):
        content_service.get_contents.return_value = ContentList(total=0, data=[])

        response = client.get(BASE_URL, params={"specs": raw})

        assert response.status_code == status.HTTP_200_OK
        assert content_service.get_contents.await_args.kwargs["specs"] == parsed

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            "not json",
            "{color: red}",
            '{"color": "red"',
            "[1, 2]",
            '"red"',
            "5",
            "true",
            "null",
        ],
    )
    def test_rejects_invalid_specs_filter(
        self,
        client: TestClient,
        content_service: ContentService,
        raw: str,
    ):
        response = client.get(BASE_URL, params={"specs": raw})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json() == SPECS_FORMAT_ERROR
        content_service.get_contents.assert_not_awaited()

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
        content_service: ContentService,
        params: dict[str, str],
    ):
        response = client.get(BASE_URL, params=params)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        content_service.get_contents.assert_not_awaited()


class TestGetContent:
    def test_returns_content(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
    ):
        content = content_factory()
        content_service.get_content.return_value = content

        response = client.get(f"{BASE_URL}/{CONTENT_ID}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _json(content)
        content_service.get_content.assert_awaited_once_with(
            content_id=CONTENT_ID,
        )

    def test_response_keeps_all_fields(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
    ):
        content_service.get_content.return_value = content_factory()

        response = client.get(f"{BASE_URL}/{CONTENT_ID}")

        assert set(response.json()) == set(ContentOut.model_fields)

    def test_not_found(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        content_service.get_content.side_effect = NotFoundError(
            resource="Content",
            identifier=CONTENT_ID,
        )

        response = client.get(f"{BASE_URL}/{CONTENT_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": f"Content '{CONTENT_ID}' not found"}


class TestCreateContent:
    def test_creates_content(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
        create_payload: dict[str, Any],
    ):
        content = content_factory()
        content_service.create_content.return_value = content

        response = client.post(BASE_URL, json=create_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == _json(content)

    def test_forwards_parsed_payload(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
        create_payload: dict[str, Any],
    ):
        content_service.create_content.return_value = content_factory()

        client.post(BASE_URL, json=create_payload)

        content_service.create_content.assert_awaited_once_with(
            payload=ContentCreate(**create_payload),
        )

    def test_ignores_read_only_fields(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
        create_payload: dict[str, Any],
    ):
        content_service.create_content.return_value = content_factory()

        response = client.post(
            BASE_URL,
            json={
                **create_payload,
                "id": "client-chosen-id",
                "created_at": "2000-01-01T00:00:00Z",
                "active": False,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        content_service.create_content.assert_awaited_once_with(
            payload=ContentCreate(**create_payload),
        )

    def test_accepts_null_specs(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
        create_payload: dict[str, Any],
    ):
        content_service.create_content.return_value = content_factory(specs=None)

        response = client.post(BASE_URL, json={**create_payload, "specs": None})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["specs"] is None

    @pytest.mark.parametrize("missing_field", ["identifier", "specs"])
    def test_rejects_missing_required_field(
        self,
        client: TestClient,
        content_service: ContentService,
        create_payload: dict[str, Any],
        missing_field: str,
    ):
        del create_payload[missing_field]

        response = client.post(BASE_URL, json=create_payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0]["loc"] == ["body", missing_field]
        content_service.create_content.assert_not_awaited()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("identifier", None),
            ("identifier", 123),
            ("specs", "fast"),
            ("specs", [1, 2]),
        ],
    )
    def test_rejects_invalid_field(
        self,
        client: TestClient,
        content_service: ContentService,
        create_payload: dict[str, Any],
        field: str,
        value: Any,
    ):
        response = client.post(BASE_URL, json={**create_payload, field: value})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0]["loc"][:2] == ["body", field]
        content_service.create_content.assert_not_awaited()

    def test_rejects_non_json_body(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        response = client.post(
            BASE_URL,
            content="not json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        content_service.create_content.assert_not_awaited()


class TestSetContentSpecs:
    URL = f"{BASE_URL}/{CONTENT_ID}/specs"

    def test_sets_specs(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
    ):
        content = content_factory(specs={"color": "blue", "size": 5})
        content_service.set_content_specs.return_value = content

        response = client.put(self.URL, json={"specs": {"color": "blue"}})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _json(content)
        content_service.set_content_specs.assert_awaited_once_with(
            content_id=CONTENT_ID,
            payload=ContentSetSpecs(specs={"color": "blue"}),
        )

    @pytest.mark.parametrize(
        "specs",
        [
            {},
            {"meta": {"a": 1}, "tags": ["x", "y"], "gone": None},
        ],
    )
    def test_accepts_any_specs_object(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
        specs: dict[str, Any],
    ):
        content_service.set_content_specs.return_value = content_factory()

        response = client.put(self.URL, json={"specs": specs})

        assert response.status_code == status.HTTP_200_OK
        payload = content_service.set_content_specs.await_args.kwargs["payload"]
        assert payload.specs == specs

    def test_ignores_other_fields(
        self,
        client: TestClient,
        content_service: ContentService,
        content_factory: ContentFactory,
    ):
        content_service.set_content_specs.return_value = content_factory()

        response = client.put(
            self.URL,
            json={"specs": {"color": "blue"}, "identifier": "renamed"},
        )

        assert response.status_code == status.HTTP_200_OK
        content_service.set_content_specs.assert_awaited_once_with(
            content_id=CONTENT_ID,
            payload=ContentSetSpecs(specs={"color": "blue"}),
        )

    def test_not_found(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        content_service.set_content_specs.side_effect = NotFoundError(
            resource="Content",
            identifier=CONTENT_ID,
        )

        response = client.put(self.URL, json={"specs": {"color": "blue"}})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": f"Content '{CONTENT_ID}' not found"}

    @pytest.mark.parametrize(
        "body",
        [
            {},
            {"specs": None},
            {"specs": "fast"},
            {"specs": [1, 2]},
        ],
    )
    def test_rejects_invalid_specs(
        self,
        client: TestClient,
        content_service: ContentService,
        body: dict[str, Any],
    ):
        response = client.put(self.URL, json=body)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0]["loc"][:2] == ["body", "specs"]
        content_service.set_content_specs.assert_not_awaited()

    def test_rejects_missing_body(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        response = client.put(self.URL)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        content_service.set_content_specs.assert_not_awaited()

    def test_has_no_full_replace_route(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        response = client.put(
            f"{BASE_URL}/{CONTENT_ID}",
            json={"specs": {"color": "blue"}},
        )

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert not content_service.method_calls


class TestDeleteContent:
    def test_deletes_content(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        content_service.delete_content.return_value = None

        response = client.delete(f"{BASE_URL}/{CONTENT_ID}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        content_service.delete_content.assert_awaited_once_with(
            content_id=CONTENT_ID,
        )

    def test_not_found(
        self,
        client: TestClient,
        content_service: ContentService,
    ):
        content_service.delete_content.side_effect = NotFoundError(
            resource="Content",
            identifier=CONTENT_ID,
        )

        response = client.delete(f"{BASE_URL}/{CONTENT_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": f"Content '{CONTENT_ID}' not found"}


ALL_ROUTES = [
    ("GET", BASE_URL),
    ("GET", f"{BASE_URL}/{CONTENT_ID}"),
    ("POST", BASE_URL),
    ("PUT", f"{BASE_URL}/{CONTENT_ID}/specs"),
    ("DELETE", f"{BASE_URL}/{CONTENT_ID}"),
]


@pytest.fixture
def stub_service(content_service: ContentService) -> ContentService:
    """Every service method fails fast, so any authorized request ends cleanly."""
    for name in (
        "get_contents",
        "get_content",
        "create_content",
        "set_content_specs",
        "delete_content",
    ):
        getattr(content_service, name).side_effect = NotFoundError(
            resource="Content",
            identifier="stub",
        )
    return content_service


@pytest.mark.parametrize(("method", "url"), ALL_ROUTES)
class TestAuth:
    def test_rejects_missing_key(
        self,
        anon_client: TestClient,
        content_service: ContentService,
        method: str,
        url: str,
    ):
        response = anon_client.request(method, url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.headers["WWW-Authenticate"] == "ApiKey"
        assert not content_service.method_calls

    def test_rejects_wrong_key(
        self,
        anon_client: TestClient,
        content_service: ContentService,
        method: str,
        url: str,
    ):
        response = anon_client.request(
            method,
            url,
            headers={"X-API-Key": "wrong-key"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not content_service.method_calls

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
