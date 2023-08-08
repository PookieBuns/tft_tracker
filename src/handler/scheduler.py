from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from src.settings import settings
from src.utils import create_db_url
from pydantic import PostgresDsn
from src.models import GameStatus, Player, Game

DB_URL = create_db_url(settings, "postgresql+asyncpg", PostgresDsn)


async def get_need_dispatch_players(limit: int) -> list[Player]:
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        stmt = (
            select(Player).where(Player.next_sync_time < datetime.utcnow()).limit(limit)
        )
        result = await conn.execute(stmt)
        return [Player.from_orm(player) for player in result]


async def get_need_dispatch_games(limit: int) -> list[Game]:
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        stmt = select(Game).where(Game.status == GameStatus.pending).limit(limit)
        result = await conn.execute(stmt)
        return [Game.from_orm(game) for game in result]
