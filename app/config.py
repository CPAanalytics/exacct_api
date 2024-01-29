import os

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    asyncpg_url: PostgresDsn = os.getenv("SQL_URL")
    redis_url: RedisDsn = os.getenv("REDIS_URL")
    warehouse_url: PostgresDsn = os.getenv("WSQL_URL")


settings = Settings()
