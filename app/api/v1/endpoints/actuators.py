"""# Actuators.

Actuator endpoints are placed in here.
"""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_actuator_service
from app.schemas.actuator import ActuatorCreate, ActuatorList, ActuatorOut
from app.services.actuator_service import ActuatorService

router = APIRouter(prefix="/actuators", tags=["actuators"])


@router.get(
    "",
    response_model=ActuatorList,
    status_code=status.HTTP_200_OK,
    description="It lists all actuators.",
)
async def get_actuators(  # noqa: ANN201
    page: int = 1,
    limit: int = 10,
    ascending: bool = False,
    latest: bool | None = None,
    service: ActuatorService = Depends(get_actuator_service),
):
    """# Get Actuators."""
    return await service.get_actuators(
        page=page,
        limit=limit,
        ascending=ascending,
        latest=latest,
    )


@router.get(
    "/{actuator_id}",
    response_model=ActuatorOut,
    status_code=status.HTTP_200_OK,
    description="It gets the requested actuator.",
)
async def get_actuator(  # noqa: ANN201
    actuator_id: str,
    service: ActuatorService = Depends(get_actuator_service),
):
    """# Get Actuator."""
    return await service.get_actuator(
        actuator_id=actuator_id,
    )


@router.get(
    "/{actuator_name}/latest",
    response_model=ActuatorOut,
    status_code=status.HTTP_200_OK,
    description="It gets the latest actuator for the given name",
)
async def get_latest_actuator(  # noqa: ANN201
    actuator_name: str,
    service: ActuatorService = Depends(get_actuator_service),
):
    """# Get Latest Actuator."""
    return await service.get_latest_actuator(
        actuator_name=actuator_name,
    )


@router.post(
    "",
    response_model=ActuatorOut,
    status_code=status.HTTP_201_CREATED,
    description="It creates a new actuator",
)
async def create_actuator(  # noqa: ANN201
    payload: ActuatorCreate,
    service: ActuatorService = Depends(get_actuator_service),
):
    """# Create Actuator."""
    return await service.create_actuator(
        payload=payload,
    )


@router.put(
    "/{actuator_id}",
    response_model=ActuatorOut,
    status_code=status.HTTP_200_OK,
    description="It updates the latest actuator for the name",
)
async def set_latest_actuator(  # noqa: ANN201
    actuator_id: str,
    service: ActuatorService = Depends(get_actuator_service),
):
    """# Set Latest Actuator."""
    return await service.set_latest_actuator(
        actuator_id=actuator_id,
    )


@router.delete(
    "/{actuator_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="It deletes the requested actuator",
)
async def delete_actuator(  # noqa: ANN201
    actuator_id: str,
    service: ActuatorService = Depends(get_actuator_service),
):
    """# Delete Actuator."""
    return await service.delete_actuator(
        actuator_id=actuator_id,
    )
