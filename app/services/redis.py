from redis.client import Redis
import redis

from app.core.config import RedisSettings, settings
from app.core.logger import logger  # <- import logger

redis_settings: RedisSettings = settings.redis


class RedisManager:

    def __init__(self) -> None:
        self.redis_url: str = redis_settings.url
        self.redis_use: bool = redis_settings.use
        self.redis_client: Redis | None = None
        logger.info(f"RedisManager initialized (use_redis={self.redis_use})")

    async def connect(self) -> Redis:
        if not self.redis_use:
            logger.warning("Redis usage is disabled by configuration")
            raise PermissionError("Redis usage is disabled")

        if self.redis_client is not None:
            logger.debug("Reusing existing Redis client")
            return self.redis_client

        try:
            self.redis_client = redis.Redis.from_url(self.redis_url)
            # Force a connection test
            self.redis_client.ping()
            logger.info(f"Successfully connected to Redis at {self.redis_url}")
            return self.redis_client

        except redis.ConnectionError as e:
            self.redis_client = None
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError("Failed to connect to Redis") from e

        except redis.RedisError as e:
            self.redis_client = None
            logger.error(f"Redis error occurred: {e}")
            raise RuntimeError("Redis error occurred") from e

        except Exception as e:
            self.redis_client = None
            logger.exception("Unexpected error while connecting to Redis")
            raise

    async def close(self) -> None:
        try:
            if self.redis_client is not None:
                self.redis_client.close()
                logger.info("Redis connection closed")
            else:
                logger.debug("Redis close() called but client was not connected")

        except Exception as e:
            logger.exception("Error while closing Redis connection")
            raise RuntimeError("Error while closing Redis connection") from e

        finally:
            self.redis_client = None
