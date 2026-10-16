"""# Data.

It contains the schema for data.
"""

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class DataBase(BaseModel):
    """# Data Base.

    Base class for data items.
    """

    actuator_id: str = Field(
        description="Used actuator for the data.",
    )
    metadata: object = Field(
        description="The output created with actuator.",
    )
    linked_resource: str | None = Field(
        description="The identifier for the original input.",
    )
    specs: Dict[str, Any] | None = Field(
        description="Extra information about the data.",
    )


class DataCreate(DataBase):
    """# Data Create."""

    pass


class DataOut(DataBase):
    """# Data Out."""

    id: str = Field(
        description="Data ID information",
    )
    created_at: datetime = Field(
        description="The created time for the data.",
    )
    updated_at: datetime = Field(
        description="The last updated time for the data.",
    )


class DataUpdate(BaseModel):
    """# Data Update."""

    linked_resource: str | None = Field(
        description="The identifier for the original input.",
        default=None,
    )
    specs: Dict[str, Any] | None = Field(
        description="Extra information about the data.",
        default=None,
    )


class DataList(BaseModel):
    """# Data List."""

    total: int = Field(
        description="Total data count",
    )
    data: List[DataOut] = Field(
        description="The data list",
    )
