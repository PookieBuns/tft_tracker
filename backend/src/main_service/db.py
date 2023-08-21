from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import create_async_engine

from shared.settings import settings
from shared.utils import create_db_url

DB_URL = create_db_url(settings, "postgresql+asyncpg", PostgresDsn)

engine = create_async_engine(DB_URL, pool_pre_ping=True)


async def get_connection():
    async with engine.begin() as conn:
        yield conn
