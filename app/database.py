from asyncio import current_task, TaskGroup
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from fastapi import Request
from app.config import settings as global_settings
from app.utils.logging import AppLogger
from typing import Dict
from typing import Iterable
from sqlalchemy.ext.asyncio import async_scoped_session

logger = AppLogger().get_logger()

##############################################################################################################
# Warehouse database
warehouse_cache: Dict[str, any] = {}


async def _close_sessions(db_sessions: Iterable[AsyncSession]):
    async with TaskGroup() as task_group:
        for db_session in db_sessions:
            task_group.create_task(db_session.close())


def _get_current_task_id() -> int:
    return id(current_task())


class DBManager:
    def __init__(self, async_session_factory):
        self.scoped_session_factory = async_scoped_session(
            async_session_factory,
            scopefunc=_get_current_task_id
        )

    def get_session(self) -> AsyncSession:
        return self.scoped_session_factory()


async def get_warehouse_engine(db_string: str) -> any:
    if db_string not in warehouse_cache:
        warehouse_engine = create_async_engine(
            db_string,
            future=True,
            echo=True,
        )
        warehouse_cache[db_string] = warehouse_engine
    return warehouse_cache[db_string]


# Updated Dependency
async def get_warehouse(request: Request) -> DBManager:
    db_string = global_settings.warehouse_url.unicode_string() + request.state.user['tenant_db']
    warehouse_engine = await get_warehouse_engine(db_string)
    async_session_factory = async_sessionmaker(
        warehouse_engine,
        autoflush=False,
        expire_on_commit=False,
    )
    db_manager = DBManager(async_session_factory)
    try:
        yield db_manager
    finally:
        sessions = db_manager.scoped_session_factory.registry.registry.values()
        await _close_sessions(sessions)


##############################################################################################################
# Application database

engine = create_async_engine(
    global_settings.asyncpg_url.unicode_string(),
    future=True,
    echo=True,
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)


# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        # logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        yield session
