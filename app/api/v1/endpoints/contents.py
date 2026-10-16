"""# Contents.

Content endpoints are placed in here.
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_content_service
from app.core.exceptions import InvalidFormatError
from app.schemas.contents import ContentCreate, ContentList, ContentOut, ContentSetSpecs
from app.services.content_service import ContentService

router = APIRouter(prefix="/contents", tags=["contents"])


def _parse_specs(specs: str | None) -> dict[str, Any] | None:
    """# Parse Specs.

    Parse the specs filter from a JSON object string.

    Args:
        specs: The specs filter as a JSON object, for example
            `{"color": "red", "size": 5}`. It can be None.

    Returns:
        The specs filter as a dict, or None if it is not given.

    Raises:
        InvalidFormatError: If the value is not a valid JSON object.
    """
    if specs is None:
        return None

    try:
        parsed = json.loads(specs)
    except json.JSONDecodeError as exc:
        raise InvalidFormatError(
            field="specs",
            expected="a valid JSON object",
        ) from exc

    if not isinstance(parsed, dict):
        raise InvalidFormatError(
            field="specs",
            expected="a valid JSON object",
        )

    return parsed


@router.get(
    "",
    response_model=ContentList,
    status_code=status.HTTP_200_OK,
    description="It lists all content items.",
)
async def get_contents(  # noqa: ANN201
    page: int = 1,
    limit: int = 10,
    ascending: bool = False,
    specs: str | None = Query(
        default=None,
        description=(
            "Filter by specs as a JSON object, for example "
            '{"color": "red", "size": 5}. Each key must be equal to its value.'
        ),
    ),
    service: ContentService = Depends(get_content_service),
):
    """# Get Contents."""
    return await service.get_contents(
        page=page,
        limit=limit,
        ascending=ascending,
        specs=_parse_specs(specs=specs),
    )


@router.get(
    "/{content_id}",
    response_model=ContentOut,
    status_code=status.HTTP_200_OK,
    description="It gets the requested content item.",
)
async def get_content(  # noqa: ANN201
    content_id: str,
    service: ContentService = Depends(get_content_service),
):
    """# Get Content."""
    return await service.get_content(
        content_id=content_id,
    )


@router.post(
    "",
    response_model=ContentOut,
    status_code=status.HTTP_201_CREATED,
    description="It creates a new content item.",
)
async def create_content(  # noqa: ANN201
    payload: ContentCreate,
    service: ContentService = Depends(get_content_service),
):
    """# Create Content."""
    return await service.create_content(
        payload=payload,
    )


@router.put(
    "/{content_id}/specs",
    response_model=ContentOut,
    status_code=status.HTTP_200_OK,
    description=(
        "It adds or changes the given specs keys of the content item. "
        "The other keys do not change."
    ),
)
async def set_content_specs(  # noqa: ANN201
    content_id: str,
    payload: ContentSetSpecs,
    service: ContentService = Depends(get_content_service),
):
    """# Set Content Specs."""
    return await service.set_content_specs(
        content_id=content_id,
        payload=payload,
    )


@router.delete(
    "/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="It deletes the requested content item.",
)
async def delete_content(  # noqa: ANN201
    content_id: str,
    service: ContentService = Depends(get_content_service),
):
    """# Delete Content."""
    return await service.delete_content(
        content_id=content_id,
    )
