"""# Content Repository.

It contains the Mongo DB queries for contents.
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


class ContentRepository:
    """# Content Repository."""

    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db["contents"]

    async def create(self, data: dict) -> dict:
        """# Create.

        Add the timestamps to the content and insert it into the collection.
        The service validates the input before it calls this method.

        Args:
            data: The content item from `ContentCreate`, as a dict.

        Returns:
            The stored document. It contains `id`, `created_at` and
            `updated_at`, so it is valid for `ContentOut`.
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
        logger.info("Created content %s", doc["id"])

        # Return the stored document.
        return doc

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        ascending: bool = False,
        specs: dict[str, Any] | None = None,
    ) -> dict:
        """# Get All.

        Get one page of active content items from the collection.

        Args:
            page: The page number. The first page is 1.
            limit: The number of items on one page.
            ascending: If True, sort from oldest to newest. If False, sort
                from newest to oldest.
            specs: If given, get only the items whose specs are equal to
                these values. Each key is compared with its value. An item
                must match all the keys.

        Returns:
            A dict with `total` (the count of all matching items) and `data`
            (the items on this page). It is valid for `ContentList`.
        """
        # Include only the active items.
        filter_dict: dict[str, Any] = {
            "active": True,
        }

        # Find the page start from the page number and the page size.
        skip = (page - 1) * limit

        # Set the sort direction.
        sort_direction = 1 if ascending else -1

        # Filter by each spec key. `$eq` makes sure that a value is compared
        # as it is, and is not read as a query operator.
        if specs:
            for key, value in specs.items():
                filter_dict[f"specs.{key}"] = {
                    "$eq": value,
                }

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
        logger.debug("Fetched %d of %d content items", len(docs), total)

        return {
            "total": total,
            "data": docs,
        }

    async def get(
        self,
        content_id: str,
    ) -> dict | None:
        """# Get.

        Get one active content item by its ID.

        Args:
            content_id: The ID of the content item.

        Returns:
            The content item, or None if the ID is not valid or no active
            item has this ID.
        """
        # Validate the ID. Return None if it is not valid.
        oid = _oid(content_id)
        if oid is None:
            return None

        # Find the active item. Return None if it is not found.
        doc = await self.collection.find_one(
            {
                "_id": oid,
                "active": True,
            },
        )
        if doc is None:
            return None

        doc["id"] = str(doc["_id"])
        return doc

    async def update_specs(
        self,
        content_id: str,
        specs: dict[str, Any],
    ) -> dict | None:
        """# Update Specs.

        Merge the given specs into the specs of one active content item.
        A key that already exists gets the new value. A new key is added.
        The other keys do not change.

        Args:
            content_id: The ID of the content item.
            specs: The keys and values to add or change.

        Returns:
            The updated content item, or None if the ID is not valid or no
            active item has this ID.
        """
        # Validate the ID. Return None if it is not valid.
        oid = _oid(content_id)
        if oid is None:
            return None
        filter_dict = {
            "_id": oid,
            "active": True,
        }

        # Merge the specs and return the item. Return None if it is not found.
        # The pipeline update also works when the stored specs are None.
        # `$literal` makes sure that a value is not read as an expression.
        if specs:
            doc = await self.collection.find_one_and_update(
                filter_dict,
                [
                    {
                        "$set": {
                            "specs": {
                                "$mergeObjects": [
                                    {
                                        "$ifNull": ["$specs", {}],
                                    },
                                    {
                                        "$literal": specs,
                                    },
                                ],
                            },
                            "updated_at": datetime.now(UTC),
                        },
                    },
                ],
                return_document=ReturnDocument.AFTER,
            )
        else:
            doc = await self.collection.find_one(filter_dict)
        if doc is None:
            return None

        doc["id"] = str(doc["_id"])
        logger.info("Updated specs of content %s", doc["id"])
        return doc

    async def delete_content(
        self,
        content_id: str,
    ) -> None:
        """# Delete Content.

        Soft delete one active content item. It sets `active` to False.

        Args:
            content_id: The ID of the content item.
        """
        # Validate the ID. Do nothing if it is not valid.
        oid = _oid(content_id)
        if oid is None:
            return

        await self.collection.update_one(
            {
                "_id": oid,
                "active": True,
            },
            {
                "$set": {
                    "active": False,
                    "updated_at": datetime.now(UTC),
                },
            },
        )
        logger.info("Deleted content %s", content_id)

    async def is_id_exists(
        self,
        content_id: str,
    ) -> bool:
        """# Is ID Exists.

        Check that an active content item has this ID.

        Args:
            content_id: The ID of the content item.

        Returns:
            True if an active item has this ID, else False.
        """
        # Validate the ID. Return False if it is not valid.
        oid = _oid(content_id)
        if oid is None:
            return False

        count = await self.collection.count_documents(
            {
                "_id": oid,
                "active": True,
            },
        )

        return count != 0
