from pydantic import BaseModel

from pydantic_settings import BaseSettings

class PostgresSettings(BaseModel):
    use: bool = True
    url: str = 'postgresql://postgres:postgres@localhost:9700/python'


class RedisSettings(BaseModel):
    use: bool = True
    url: str = "redis://:MySecretPassword@localhost:6379/0"



class MongoSettings(BaseModel):
    use: bool = True
    url: str = 'mongodb://admin:admin@localhost:27017/myapp?authSource=admin'


class KafkaSettings(BaseModel):
    use: bool = True
    broker: str = 'localhost:29092'
    client_id: str = 'python-backend'


class LoggerSettings(BaseModel):
    level: str = 'DEBUG'



class Settings(BaseSettings):
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()
    mongo: MongoSettings = MongoSettings()
    kafka: KafkaSettings = KafkaSettings()
    logger: LoggerSettings = LoggerSettings()
    app_name: str = 'Python-Boiler-Backend'

    class Config:
        env_file: str = '.env'

        env_nested_delimiter: str = '__'


settings: Settings = Settings()




