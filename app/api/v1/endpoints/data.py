"""# Data.

Data endpoints are placed in here.
"""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_data_service
from app.schemas.data import DataCreate, DataList, DataOut, DataUpdate
from app.services.data_service import DataService

router = APIRouter(prefix="/data", tags=["data"])


@router.get(
    "",
    response_model=DataList,
    status_code=status.HTTP_200_OK,
    description="It lists all data items.",
)
async def get_data_list(  # noqa: ANN201
    page: int = 1,
    limit: int = 10,
    ascending: bool = False,
    actuator_id: str | None = None,
    service: DataService = Depends(get_data_service),
):
    """# Get Data List."""
    return await service.get_data_list(
        page=page,
        limit=limit,
        ascending=ascending,
        actuator_id=actuator_id,
    )


@router.get(
    "/{data_id}",
    response_model=DataOut,
    status_code=status.HTTP_200_OK,
    description="It gets the requested data item.",
)
async def get_data(  # noqa: ANN201
    data_id: str,
    metadata_only: bool = False,
    service: DataService = Depends(get_data_service),
):
    """# Get Data."""
    return await service.get_data(
        data_id=data_id,
        metadata_only=metadata_only,
    )


@router.post(
    "",
    response_model=DataOut,
    status_code=status.HTTP_201_CREATED,
    description="It creates a new data item from the latest actuator.",
)
async def create_data(  # noqa: ANN201
    payload: DataCreate,
    service: DataService = Depends(get_data_service),
):
    """# Create Data."""
    return await service.create_data(
        payload=payload,
    )


@router.put(
    "/{data_id}",
    response_model=DataOut,
    status_code=status.HTTP_200_OK,
    description="It updates the linked resource and specs of the data item.",
)
async def update_data(  # noqa: ANN201
    data_id: str,
    payload: DataUpdate,
    service: DataService = Depends(get_data_service),
):
    """# Update Data."""
    return await service.update_data(
        data_id=data_id,
        payload=payload,
    )


@router.delete(
    "/{data_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="It deletes the requested data item.",
)
async def delete_data(  # noqa: ANN201
    data_id: str,
    service: DataService = Depends(get_data_service),
):
    """# Delete Data."""
    return await service.delete_data(
        data_id=data_id,
    )
