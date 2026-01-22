# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import api_routes_router as api_router
from app.core.logger import logger
from app.services.kafka import KafkaManager
from app.services.postgres import PostgresManager
from app.services.redis import RedisManager
from app.services.mongo import MongoManager

# Managers (singletons)
postgres_manager = PostgresManager()
redis_manager = RedisManager()
mongo_manager = MongoManager()
kafka_manager = KafkaManager()

# Global connection objects
postgres_cursor = None
mongo_client = None
redis_client = None
kafka_producer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global postgres_cursor, mongo_client, redis_client, kafka_producer

    try:
        if postgres_manager.use_postgres:
            postgres_cursor = await postgres_manager.connect()

        if mongo_manager.mongo_use:
            mongo_client = await mongo_manager.connect()

        if redis_manager.redis_use:
            redis_client = await redis_manager.connect()

        yield

    finally:
        if postgres_cursor:
            await postgres_manager.close_connection()
        if mongo_client:
            await mongo_manager.disconnect()
        if redis_client:
            await redis_manager.close()
        if kafka_manager.use_kafka:
            await kafka_manager.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(router=api_router, prefix="/api")
