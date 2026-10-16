"""# Data Service.

It contains the services for data.
"""

import logging

from app.core.exceptions import NotFoundError
from app.repositories.actuator_repository import ActuatorRepository
from app.repositories.data_repository import DataRepository
from app.schemas.data import DataCreate, DataList, DataOut, DataUpdate

logger = logging.getLogger(__name__)


class DataService:
    """# Data Service."""

    def __init__(
        self,
        repo: DataRepository,
        actuator_repo: ActuatorRepository,
    ):
        self.repo: DataRepository = repo
        self.actuator_repo = actuator_repo

    async def get_data_list(
        self,
        page: int = 1,
        limit: int = 10,
        ascending: bool = False,
        actuator_id: str | None = None,
    ) -> DataList:
        """# Get Data List."""
        response = await self.repo.get_all(
            page=page,
            limit=limit,
            ascending=ascending,
            actuator_id=actuator_id,
        )

        return DataList.model_validate(response)

    async def get_data(
        self,
        data_id: str,
        metadata_only: bool = False,
    ) -> DataOut:
        """# Get Data."""
        doc = await self.repo.get(
            data_id=data_id,
            metadata_only=metadata_only,
        )

        if doc is None:
            raise NotFoundError(
                resource="Data",
                identifier=data_id,
            )

        return DataOut.model_validate(doc)

    async def create_data(
        self,
        payload: DataCreate,
    ) -> DataOut:
        """# Create Data."""
        # Make sure the data comes from the latest active actuator.
        is_latest = await self.actuator_repo.is_actuator_latest(
            actuator_id=payload.actuator_id,
        )
        if not is_latest:
            logger.warning(
                "Rejected data for actuator %s: not the latest active version",
                payload.actuator_id,
            )
            raise NotFoundError(
                resource="Actuator",
                identifier=payload.actuator_id,
            )

        # Insert the data item into the collection.
        doc = await self.repo.create(
            data=payload.model_dump(),
        )

        # Return the stored data item.
        return DataOut.model_validate(doc)

    async def update_data(
        self,
        data_id: str,
        payload: DataUpdate,
    ) -> DataOut:
        """# Data Out."""
        is_id_exists = await self.repo.is_id_exist(
            data_id=data_id,
        )

        if is_id_exists is False:
            raise NotFoundError(
                resource="Data",
                identifier=data_id,
            )

        doc = self.repo.update(
            data_id=data_id,
            linked_resource=payload.linked_resource,
            specs=payload.specs,
        )

        return DataOut.model_validate(doc)

    async def delete_data(
        self,
        data_id: str,
    ) -> None:
        """# Delete Data."""
        is_id_exists = await self.repo.is_id_exist(
            data_id=data_id,
        )

        if is_id_exists is False:
            raise NotFoundError(
                resource="Data",
                identifier=data_id,
            )

        self.repo.delete_actuator(
            data_id=data_id,
        )
