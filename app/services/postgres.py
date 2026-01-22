import psycopg2
from psycopg2.extensions import connection as PGConnection, cursor as PGCursor
from psycopg2 import OperationalError, DatabaseError

from app.core.config import PostgresSettings, settings
from app.core.logger import logger  # <- import logger

postgres_settings: PostgresSettings = settings.postgres


class PostgresManager:

    def __init__(self) -> None:
        self.database_url: str = postgres_settings.url
        self.use_postgres: bool = postgres_settings.use
        self.database_connection: PGConnection | None = None
        self.database_cursor: PGCursor | None = None
        logger.info(f"PostgresManager initialized (use_postgres={self.use_postgres})")

    async def connect(self) -> PGCursor:
        if not self.use_postgres:
            logger.warning("Postgres usage is disabled")
            raise PermissionError("Postgres usage is disabled")

        if self.database_connection and self.database_cursor:
            logger.debug("Reusing existing PostgreSQL connection")
            return self.database_cursor

        try:
            self.database_connection = psycopg2.connect(self.database_url)
            self.database_cursor = self.database_connection.cursor()
            logger.info("Successfully connected to PostgreSQL")
            return self.database_cursor

        except OperationalError as e:
            self._cleanup()
            logger.error(f"Failed to connect to PostgreSQL (OperationalError): {e}")
            raise RuntimeError("Failed to connect to PostgreSQL") from e

        except DatabaseError as e:
            self._cleanup()
            logger.error(f"Database error occurred: {e}")
            raise RuntimeError("Database error occurred") from e

        except Exception as e:
            self._cleanup()
            logger.exception("Unexpected error while connecting to PostgreSQL")
            raise

    async def close_connection(self) -> None:
        try:
            if self.database_cursor is not None:
                self.database_cursor.close()
                logger.info("PostgreSQL cursor closed")

            if self.database_connection is not None:
                self.database_connection.close()
                logger.info("PostgreSQL connection closed")

        except Exception as e:
            logger.exception("Error while closing PostgreSQL connection")
            raise RuntimeError("Error while closing PostgreSQL connection") from e

        finally:
            self.database_cursor = None
            self.database_connection = None

    def _cleanup(self) -> None:
        """Internal helper to safely clean up resources"""
        try:
            if self.database_cursor:
                self.database_cursor.close()
            if self.database_connection:
                self.database_connection.close()
        finally:
            self.database_cursor = None
            self.database_connection = None
            logger.debug("PostgreSQL resources cleaned up")
