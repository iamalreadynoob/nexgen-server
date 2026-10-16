"""# Actuator Service.

It contains the services for actuators.
"""

from app.core.exceptions import (
    AlreadyExistsError,
    LatestDeletionError,
    NotFoundError,
)
from app.repositories.actuator_repository import ActuatorRepository
from app.schemas.actuator import ActuatorCreate, ActuatorList, ActuatorOut


class ActuatorService:
    """# Actuator Service."""

    def __init__(self, repo: ActuatorRepository):
        self.repo: ActuatorRepository = repo

    async def get_actuators(
        self,
        page: int = 1,
        limit: int = 10,
        ascending: bool = False,
        latest: bool | None = None,
        name: str | None = None,
    ) -> ActuatorList:
        """# Get Actuators."""
        response = await self.repo.get_all(
            page=page,
            limit=limit,
            ascending=ascending,
            latest=latest,
            name=name,
        )

        return ActuatorList.model_validate(response)

    async def get_actuator(
        self,
        actuator_id: str,
    ) -> ActuatorOut:
        """# Get Actuator."""
        doc = await self.repo.get(
            actuator_id=actuator_id,
        )

        if doc is None:
            raise NotFoundError(
                resource="Actuator",
                identifier=actuator_id,
            )

        return ActuatorOut.model_validate(doc)

    async def get_latest_actuator(
        self,
        actuator_name: str,
    ) -> ActuatorOut:
        """# Get Latest Actuator."""
        doc = await self.repo.get_latest(
            actuator_name=actuator_name,
        )

        if doc is None:
            raise NotFoundError(
                resource="Actuator",
                identifier=actuator_name,
            )

        return ActuatorOut.model_validate(doc)

    async def create_actuator(
        self,
        payload: ActuatorCreate,
    ) -> ActuatorOut:
        """# Create Actuator."""
        is_taken = await self.repo.is_actuator_taken(
            actuator_name=payload.name,
            actuator_version=payload.version,
        )

        if is_taken is True:
            raise AlreadyExistsError(
                resource="Actuator",
                identifier=f"{payload.name} ({payload.version})",
            )

        data = payload.model_dump()
        data["latest"] = data["set_latest"]
        del data["set_latest"]

        is_name_exist = await self.repo.is_name_exist(
            actuator_name=payload.name,
        )

        if is_name_exist is False:
            data["latest"] = True

        if data["latest"] is True:
            await self._clear_latest(
                actuator_name=payload.name,
            )

        doc = await self.repo.create(
            data=data,
        )

        return ActuatorOut.model_validate(doc)

    async def set_latest_actuator(
        self,
        actuator_id: str,
    ) -> ActuatorOut:
        """# Set Latest Actuator."""
        actuator = await self.repo.get(
            actuator_id=actuator_id,
        )

        if actuator is None:
            raise NotFoundError(
                resource="Actuator",
                identifier=actuator_id,
            )

        if actuator["latest"] is True:
            raise AlreadyExistsError(
                resource="Actuator",
                identifier=f"{actuator_id} (latest: True)",
            )

        await self._clear_latest(
            actuator_name=actuator["name"],
        )

        doc = await self.repo.change_latest_info(
            actuator_id=actuator_id,
            latest=True,
        )

        return ActuatorOut.model_validate(doc)

    async def delete_actuator(
        self,
        actuator_id: str,
    ) -> None:
        """# Delete Actuator."""
        is_id_exists = await self.repo.is_id_exist(
            actuator_id=actuator_id,
        )

        if is_id_exists is False:
            raise NotFoundError(
                resource="Actuator",
                identifier=actuator_id,
            )

        is_latest = await self.repo.is_actuator_latest(
            actuator_id=actuator_id,
        )

        if is_latest is True:
            raise LatestDeletionError(
                resource="Actuator",
                identifier=actuator_id,
            )

        await self.repo.delete_actuator(
            actuator_id=actuator_id,
        )

    async def _clear_latest(
        self,
        actuator_name: str,
    ) -> None:
        """# Clear Latest.

        It unmarks the current latest actuator of the name, if there is one.
        """
        current_latest = await self.repo.get_latest(
            actuator_name=actuator_name,
        )

        if current_latest is None:
            return

        await self.repo.change_latest_info(
            actuator_id=str(current_latest["_id"]),
            latest=False,
        )
