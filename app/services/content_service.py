"""# Content Service.

It contains the services for contents.
"""

import logging
from typing import Any

from app.core.exceptions import NotFoundError
from app.repositories.content_repository import ContentRepository
from app.schemas.contents import ContentCreate, ContentList, ContentOut, ContentSetSpecs

logger = logging.getLogger(__name__)


class ContentService:
    """# Content Service."""

    def __init__(
        self,
        repo: ContentRepository,
    ):
        self.repo: ContentRepository = repo

    async def create_content(
        self,
        payload: ContentCreate,
    ) -> ContentOut:
        """# Create Content."""
        # Insert the content item into the collection.
        doc = await self.repo.create(
            data=payload.model_dump(),
        )

        # Return the stored content item.
        return ContentOut.model_validate(doc)

    async def get_contents(
        self,
        page: int = 1,
        limit: int = 10,
        ascending: bool = False,
        specs: dict[str, Any] | None = None,
    ) -> ContentList:
        """# Get Contents."""
        response = await self.repo.get_all(
            page=page,
            limit=limit,
            ascending=ascending,
            specs=specs,
        )

        return ContentList.model_validate(response)

    async def get_content(
        self,
        content_id: str,
    ) -> ContentOut:
        """# Get Content."""
        is_id_exists = await self.repo.is_id_exists(
            content_id=content_id,
        )

        if is_id_exists is False:
            raise NotFoundError(
                resource="Content",
                identifier=content_id,
            )

        doc = await self.repo.get(
            content_id=content_id,
        )

        return ContentOut.model_validate(doc)

    async def set_content_specs(
        self,
        content_id: str,
        payload: ContentSetSpecs,
    ) -> ContentOut:
        """# Set Content Specs."""
        is_id_exists = await self.repo.is_id_exists(
            content_id=content_id,
        )

        if is_id_exists is False:
            raise NotFoundError(
                resource="Content",
                identifier=content_id,
            )

        doc = await self.repo.update_specs(
            content_id=content_id,
            specs=payload.specs,
        )

        return ContentOut.model_validate(doc)

    async def delete_content(
        self,
        content_id: str,
    ) -> None:
        """# Delete Content."""
        is_id_exists = await self.repo.is_id_exists(
            content_id=content_id,
        )

        if is_id_exists is False:
            raise NotFoundError(
                resource="Content",
                identifier=content_id,
            )

        await self.repo.delete_content(
            content_id=content_id,
        )
