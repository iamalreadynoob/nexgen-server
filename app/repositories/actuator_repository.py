"""# Actuator Repository.

It contains the Mongo DB queries for actuators.
"""

from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.asynchronous.collection import AsyncCollection  # noqa: TC002
from pymongo.asynchronous.database import AsyncDatabase


def _oid(value: str) -> ObjectId | None:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


class ActuatorRepository:
    """# Actuator Repository."""

    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db["actuators"]

    async def create(self, data: dict) -> dict:
        """# It creates the actuator."""
        process_time = datetime.now(UTC)
        doc = {
            **data,
            "created_at": process_time,
            "updated_at": process_time,
        }

        if data["latest"] is True:
            await self.collection.update_one(
                {
                    "name": data["name"],
                    "latest": True,
                },
                {
                    "$set": {
                        "latest": False,
                    },
                },
            )

        result = await self.collection.insert_one(doc)
        doc["id"] = result.inserted_id

        return doc

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        ascending: bool = False,
        latest: bool | None = None,
        name: str | None = None,
    ) -> dict:
        """It gets all actuators."""
        skip = (page - 1) * limit
        sort_direction = 1 if ascending else -1

        filter_dict = {
            "active": True,
        }

        if latest is not None:
            filter_dict["latest"] = latest

        if name is not None:
            filter_dict["name"] = name

        cursor = (
            self.collection.find(filter_dict)
            .sort("_id", sort_direction)
            .skip(skip)
            .limit(limit)
        )

        docs = await cursor.to_list(length=limit)
        total = await self.collection.count_documents(filter_dict)

        return {
            "total": total,
            "actuators": docs,
        }

    async def get(
        self,
        actuator_id: str,
    ) -> dict | None:
        """It gets the actuator."""
        oid = _oid(actuator_id)

        if oid is None:
            return None

        return await self.collection.find_one(
            {
                "_id": oid,
                "active": True,
            },
        )

    async def get_latest(
        self,
        actuator_name: str,
    ) -> dict | None:
        """It gets the latest one."""
        return await self.collection.find_one(
            {
                "name": actuator_name,
                "latest": True,
            },
        )

    async def set_latest(
        self,
        actuator_id: str,
    ) -> dict:
        """It changes the latest actuator."""
        oid = _oid(actuator_id)

        if oid is None:
            return None

        await self.collection.update_one(
            {
                "_id": oid,
                "active": True,
            },
            {
                "$set": {
                    "latest": True,
                },
            },
        )

        return await self.get(
            actuator_id=actuator_id,
        )

    async def delete_actuator(
        self,
        actuator_id: str,
    ) -> None:
        """It deletes the actuator."""
        oid = _oid(actuator_id)

        if oid is None:
            return None

        await self.collection.update_one(
            {
                "_id": oid,
                "active": True,
            },
            {
                "$set": {
                    "active": False,
                },
            },
        )

    async def is_id_exist(
        self,
        actuator_id: str,
    ) -> bool:
        """It checks that ID exists or not."""
        oid = _oid(actuator_id)

        if oid is None:
            return False

        count = await self.collection.count_documents(
            {
                "_id": oid,
                "active": True,
            },
        )

        return count != 0

    async def is_actuator_taken(
        self,
        actuator_name: str,
        actuator_version: str,
    ) -> bool:
        """It checks that actuator with particular name and version already created."""
        count = await self.collection.count_documents(
            {
                "name": actuator_name,
                "version": actuator_version,
                "active": True,
            },
        )

        return count != 0

    async def is_actuator_latest(
        self,
        actuator_id: str,
    ) -> bool:
        """It checks that actuator is latest or not."""
        oid = _oid(actuator_id)

        if oid is None:
            return False

        count = await self.collection.count_documents(
            {
                "_id": oid,
                "latest": True,
                "active": True,
            },
        )

        return count != 0

    async def is_name_exist(
        self,
        actuator_name: str,
    ) -> bool:
        """It checks that the actuator with that name has already been created."""
        count = await self.collection.count_documents(
            {
                "name": actuator_name,
                "active": True,
            },
        )

        return count > 0
