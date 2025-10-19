from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from .settings import settings


class MongoClientManager:
    """Manages a singleton Motor client with connection pooling."""

    _client: Optional[AsyncIOMotorClient] = None

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls._client is None:
            logger.info("Initializing MongoDB client")
            cls._client = AsyncIOMotorClient(
                settings.mongodb_uri.get_secret_value(),
                maxPoolSize=100,
                minPoolSize=0,
                serverSelectionTimeoutMS=5000,
                uuidRepresentation="standard",
                appname="m365-file-organizer",
            )
        return cls._client

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        client = cls.get_client()
        return client[settings.mongodb_database]

    @classmethod
    async def ping(cls) -> bool:
        try:
            client = cls.get_client()
            await client.admin.command("ping")
            logger.info("MongoDB ping successful")
            return True
        except ConnectionFailure as exc:  # pragma: no cover - environment-specific
            logger.error("MongoDB connection failed: {}", exc)
            return False


@asynccontextmanager
async def lifespan_mongo() -> AsyncIterator[AsyncIOMotorDatabase]:
    """Async context manager to yield DB and ensure cleanup on shutdown."""
    db = MongoClientManager.get_db()
    try:
        yield db
    finally:
        client = MongoClientManager._client
        if client is not None:
            logger.info("Closing MongoDB client")
            client.close()
            MongoClientManager._client = None
