import asyncio

import aiohttp
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import create_async_engine

from src.handler.extractor import get_game_data, get_profile_data, update_profile_data
from src.handler.loader import (
    load_augment_cache,
    load_game,
    load_game_detail,
    load_item_cache,
    load_player,
    load_unit_cache,
)
from src.handler.transformer import (
    get_update_url,
    transform_game_data,
    transform_profile_data,
)
from src.models import GameModel, Player
from src.settings import settings

DB_URL = (
    "postgresql+asyncpg://"
    f"{settings.db_user}:{settings.db_password}@"
    f"{settings.db_host}:{settings.db_port}/"
    f"{settings.db_name}"
)


async def run_single(username, region, lock):
    try:
        engine = create_async_engine(DB_URL)
        async with aiohttp.ClientSession() as session:
            async with engine.begin() as conn:
                logger.info(f"getting profile data for {username} in {region}")
                profile_data = await get_profile_data(
                    session, region=region, username=username
                )
                update_url = get_update_url(profile_data, username)
                await update_profile_data(session, update_url)
                player, games = transform_profile_data(profile_data)
                player_id = await load_player(conn, player)
                game_mdls = []
                for game in games:
                    game_id = await load_game(conn, game)
                    game_data = await get_game_data(
                        session, region, player.player_name, game.id
                    )
                    game_players = transform_game_data(game_data)
                    game_mdl = GameModel(game=game, players=game_players)
                    game_mdls.append(game_mdl)

        async with lock:
            logger.info(f"loading game data for {username} in {region}")
            async with engine.begin() as conn:
                for game_mdl in game_mdls:
                    await load_game_detail(conn, game_mdl)
        logger.success(f"done with {username} in {region}")
    except Exception as e:
        logger.warning(f"error with {username} in {region}")
        logger.exception(e)


async def run_from_db(count=10):
    engine = create_async_engine(DB_URL)
    lock = asyncio.Lock()
    async with engine.begin() as conn:
        stmt = (
            select(Player.player_name, Player.region)
            .where(Player.player_tier == None)
            .order_by(func.random())
            .limit(count)
        )
        res = await conn.execute(stmt)
        coros = []
        for player_name, region in res:
            coros.append(run_single(player_name, region, lock))
    await asyncio.gather(*coros)


async def main():
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        await load_augment_cache(conn)
        await load_unit_cache(conn)
        await load_item_cache(conn)
    while True:
        await run_from_db(5)


if __name__ == "__main__":
    # print(SQLModel.metadata.tables)
    asyncio.run(main())
