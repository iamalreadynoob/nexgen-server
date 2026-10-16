"""# Data Repository.

It contains the Mongo DB queries for data.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from pymongo.asynchronous.collection import AsyncCollection  # noqa: TC002
from pymongo.asynchronous.database import AsyncDatabase

logger = logging.getLogger(__name__)


def _oid(value: str) -> ObjectId | None:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


class DataRepository:
    """# Actuator Repository."""

    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db["data"]

    async def create(self, data: dict) -> dict:
        """# Create.

        Add the timestamps to the data and insert it into the collection.
        The service validates the input before it calls this method.

        Args:
            data: The data item from `DataCreate`, as a dict.

        Returns:
            The stored document. It contains `id`, `created_at` and
            `updated_at`, so it is valid for `DataOut`.
        """
        # Add the process time as the created and updated time.
        process_time = datetime.now(UTC)
        doc = {
            **data,
            "created_at": process_time,
            "updated_at": process_time,
            "active": True,
        }

        # Insert the document into the collection.
        result = await self.collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        logger.info("Created data %s", doc["id"])

        # Return the stored document.
        return doc

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        ascending: bool = False,
        actuator_id: str | None = None,
    ) -> dict:
        """# Get All.

        Get one page of active data items from the collection.

        Args:
            page: The page number. The first page is 1.
            limit: The number of items on one page.
            ascending: If True, sort from oldest to newest. If False, sort
                from newest to oldest.
            actuator_id: If given, get only the data made with this actuator.

        Returns:
            A dict with `total` (the count of all matching items) and `data`
            (the items on this page). It is valid for `DataList`.
        """
        # Include only the active items.
        filter_dict = {
            "active": True,
        }

        # Find the page start from the page number and the page size.
        skip = (page - 1) * limit

        # Set the sort direction.
        sort_direction = 1 if ascending else -1

        # Filter by the actuator, if one is given.
        if actuator_id is not None:
            filter_dict["actuator_id"] = actuator_id

        cursor = (
            self.collection.find(filter_dict)
            .sort("_id", sort_direction)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        total = await self.collection.count_documents(filter_dict)
        for doc in docs:
            doc["id"] = str(doc["_id"])
        logger.debug("Fetched %d of %d data items", len(docs), total)

        return {
            "total": total,
            "data": docs,
        }

    async def get(
        self,
        data_id: str,
        metadata_only: bool,
    ) -> dict | None:
        """# Get.

        Get one active data item by its ID.

        Args:
            data_id: The ID of the data item.
            metadata_only: If True, get only `id`, `actuator_id` and
                `metadata`. If False, get all the fields.

        Returns:
            The data item, or None if the ID is not valid or no active item
            has this ID.
        """
        # Validate the ID. Return None if it is not valid.
        oid = _oid(data_id)
        if oid is None:
            return None

        # Select only the metadata and the actuator ID, if metadata_only is True.
        projection = (
            {
                "actuator_id": 1,
                "metadata": 1,
            }
            if metadata_only
            else None
        )

        # Find the active item. Return None if it is not found.
        doc = await self.collection.find_one(
            {
                "_id": oid,
                "active": True,
            },
            projection=projection,
        )
        if doc is None:
            return None

        doc["id"] = str(doc["_id"])
        return doc

    async def update(
        self,
        data_id: str,
        linked_resource: str | None = None,
        specs: dict[str, Any] | None = None,
    ) -> dict | None:
        """# Update.

        Change the linked resource and the specs of one active data item.
        A field that is None does not change.

        Args:
            data_id: The ID of the data item.
            linked_resource: The new linked resource. If None, it does not
                change.
            specs: The new specs. If None, they do not change.

        Returns:
            The updated data item, or None if the ID is not valid or no
            active item has this ID.
        """
        # Validate the ID. Return None if it is not valid.
        oid = _oid(data_id)
        if oid is None:
            return None
        filter_dict = {
            "_id": oid,
            "active": True,
        }
        updates: dict[str, Any] = {}

        # Set the linked resource, if it is given.
        if linked_resource is not None:
            updates["linked_resource"] = linked_resource

        # Set the specs, if they are given.
        if specs is not None:
            updates["specs"] = specs

        # Update the active item and return it. Return None if it is not found.
        if updates:
            doc = await self.collection.find_one_and_update(
                filter_dict,
                {
                    "$set": updates,
                },
                return_document=ReturnDocument.AFTER,
            )
        else:
            doc = await self.collection.find_one(filter_dict)
        if doc is None:
            return None

        doc["id"] = str(doc["_id"])
        logger.info("Updated data %s", doc["id"])
        return doc

    async def delete_actuator(
        self,
        data_id: str,
    ) -> None:
        """It deletes the data."""
        oid = _oid(data_id)

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
