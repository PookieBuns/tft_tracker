from datetime import datetime, timedelta

from pydantic import PostgresDsn
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import col

from shared.models import Game, GameStatus, Player
from shared.settings import settings
from shared.utils import create_db_url

DB_URL = create_db_url(settings, "postgresql+asyncpg", PostgresDsn)


async def get_need_dispatch_players(limit: int) -> list[Player]:
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        stmt = (
            select(Player)
            .where(Player.next_sync_time < datetime.utcnow())
            .order_by(Player.player_rank_score)
            .limit(limit)
        )
        result = await conn.execute(stmt)
        player_list = [Player.from_orm(player) for player in result]
        player_ids = [player.id for player in player_list]
        update_stmt = (
            update(Player)
            .where(col(Player.id).in_(player_ids))
            .values(next_sync_time=datetime.utcnow() + timedelta(hours=1))
        )
        await conn.execute(update_stmt)
    return player_list


async def get_need_dispatch_games(limit: int) -> list[Game]:
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        stmt = (
            select(Game)
            .where(Game.status == GameStatus.pending)
            .order_by(func.random())
            .limit(limit)
        )
        result = await conn.execute(stmt)
        return [Game.from_orm(game) for game in result]
