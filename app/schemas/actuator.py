"""# Actuator.

It contains the schemas for the actuator.
"""

from datetime import datetime
from typing import Annotated, Dict, List, Literal

from pydantic import BaseModel, BeforeValidator, Field

# Mongo ObjectId -> str
PyObjectId = Annotated[str, BeforeValidator(str)]


class ActuatorBase(BaseModel):
    """# Actuator Base.

    Base class for actuators.
    """

    name: str = Field(
        min_length=1,
        max_length=64,
        description="Name of the actuator.",
    )
    version: str = Field(
        min_length=1,
        max_length=128,
        description="Version for the actuator.",
    )
    actuator_type: Literal["coding", "decoding"] = Field(
        description="The type of the actuator. It can be either coding or decoding",
    )
    requirements: List[str] = Field(
        description="Python modules that will be required for the actuator.",
    )
    method: str = Field(
        description="The source code for the actuator. It has to be a method.",
    )
    method_args: Dict[str, Dict[str, str]] | None = Field(
        default=None,
        description="Extra information about the method arguments.",
    )


class ActuatorCreate(ActuatorBase):
    """# Actuator Create."""

    set_latest: bool = Field(
        default=False,
        description=(
            "It either marks the created actuator latest or not. If there is no active "
            "actuator for the name then it is set as latest either way."
        ),
    )


class ActuatorOut(ActuatorBase):
    """# Actuator Output."""

    id: PyObjectId = Field(
        alias="_id",
        description="ID for the Actuator",
    )
    latest: bool = Field(
        description="It holds the latest info for the active actuator in its name",
    )
    created_at: datetime = Field(
        description="The created time for the actuator.",
    )
    updated_at: datetime = Field(
        description="The last updated time for the actuator.",
    )


class ActuatorList(BaseModel):
    """# Actuator List."""

    total: int = Field(
        description="Total actuator count.",
    )
    actuators: List[ActuatorOut] = Field(
        description="List of the actuators",
    )
