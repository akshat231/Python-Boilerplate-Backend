from app.core.config import KafkaSettings
from confluent_kafka.aio import AIOProducer, AIOConsumer
from confluent_kafka import KafkaException
from app.core.config import settings
from app.core.logger import logger

kafka_settings: KafkaSettings = settings.kafka


class KafkaManager:

    def __init__(self) -> None:
        self.broker: str = kafka_settings.broker
        self.client_id: str = kafka_settings.client_id
        self.use_kafka: bool = kafka_settings.use
        self.producers: dict[str, AIOProducer] = {}
        self.consumers: list[AIOConsumer] = []
        logger.info(f"KafkaManager initialized (use_kafka={self.use_kafka})")

    async def connect(self, default_producers: list[str] | None = None) -> dict[str, AIOProducer]:
        if not self.use_kafka:
            logger.warning("Kafka usage is disabled, skipping connection")
            return {}

        default_producers = default_producers or []

        # Initialize default producers
        for name in default_producers:
            if name not in self.producers:
                producer = AIOProducer(
                    producer_conf={
                        "bootstrap.servers": self.broker,
                        "client.id": f"{self.client_id}-{name}",
                    }
                )
                self.producers[name] = producer
                logger.info(f"Kafka producer '{name}' created at startup")

        logger.info("KafkaManager connected successfully")
        return self.producers

    def get_producer(self, name: str) -> AIOProducer:
        if not self.use_kafka:
            raise PermissionError("Kafka usage is disabled")

        if name not in self.producers:
            raise RuntimeError(f"Producer '{name}' not initialized. Call connect() first or provide default_producers.")

        return self.producers[name]

    def create_consumer(self, group_id: str, topics: list[str]) -> AIOConsumer:
        if not self.use_kafka:
            raise PermissionError("Kafka usage is disabled")

        consumer = AIOConsumer(
            consumer_conf={
                "bootstrap.servers": self.broker,
                "group.id": group_id,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )
        consumer.subscribe(topics)
        self.consumers.append(consumer)
        logger.info(f"Kafka consumer created for group '{group_id}' subscribing to {topics}")
        return consumer

    async def shutdown(self) -> None:
        logger.info("Shutting down KafkaManager...")

        for name, producer in self.producers.items():
            try:
                await producer.flush(timeout=5)
                logger.info(f"Kafka producer '{name}' flushed successfully")
            except Exception as e:
                logger.error(f"Failed to flush producer '{name}': {e}")

        for consumer in self.consumers:
            try:
                await consumer.close()
                logger.info("Kafka consumer closed successfully")
            except Exception as e:
                logger.error(f"Failed to close consumer: {e}")

        self.producers.clear()
        self.consumers.clear()
        logger.info("KafkaManager shutdown complete")
