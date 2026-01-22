from typing import Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import MongoSettings, settings
from app.core.logger import logger 

mongo_settings: MongoSettings = settings.mongo


class MongoManager:
    def __init__(self) -> None:
        self.mongo_url: str = mongo_settings.url
        self.mongo_use: bool = mongo_settings.use
        self.mongo_client: MongoClient[dict[str, Any]] | None = None
        logger.info(f"MongoManager initialized (use_mongo={self.mongo_use})")

    async def connect(self) -> MongoClient[dict[str, Any]]:
        if not self.mongo_use:
            logger.warning("MongoDB usage is disabled by configuration")
            raise PermissionError("MongoDB usage is disabled by configuration")

        if self.mongo_client is not None:
            logger.debug("MongoDB client already connected, reusing existing client")
            return self.mongo_client

        try:
            self.mongo_client = MongoClient(
                self.mongo_url,
                serverSelectionTimeoutMS=5000,
            )
            # Test connection
            self.mongo_client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB at {self.mongo_url}")
            return self.mongo_client

        except PyMongoError as exc:
            self.mongo_client = None
            logger.error(f"Failed to connect to MongoDB: {exc}")
            raise ConnectionError(f"Failed to connect to MongoDB: {exc}") from exc

    async def disconnect(self) -> None:
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")
            self.mongo_client = None
        else:
            logger.debug("MongoDB disconnect called but client was not connected")
