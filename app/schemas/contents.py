"""# Contents.

It contains the schema for contents.
"""

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ContentBase(BaseModel):
    """# Content Base.

    Base class for content items.
    """

    identifier: str = Field(
        description="The identifier for the content.",
    )
    specs: Dict[str, Any] | None = Field(
        description="Extra information about the content.",
    )


class ContentCreate(ContentBase):
    """# Content Create."""

    pass


class ContentOut(ContentBase):
    """# Content Out."""

    id: str = Field(
        description="Content ID information",
    )
    created_at: datetime = Field(
        description="The created time for the content.",
    )
    updated_at: datetime = Field(
        description="The last updated time for the content.",
    )


class ContentSetSpecs(BaseModel):
    """# Content Set Specs."""

    specs: Dict[str, Any] = Field(
        description="It adds or rewrites the values for the given keys",
    )


class ContentList(BaseModel):
    """# Content List."""

    total: int = Field(
        description="Total content count",
    )
    data: List[ContentOut] = Field(
        description="The content list",
    )
