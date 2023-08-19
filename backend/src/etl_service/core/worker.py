import asyncio
from datetime import datetime, timedelta

from aiohttp import ClientSession
from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncEngine

from etl_service.core.extractor import (
    get_match_data,
    get_match_detail_data,
    get_profile_data,
    update_profile_data,
)
from etl_service.core.loader import load_game, load_game_detail, load_player
from etl_service.core.scheduler import (
    get_need_dispatch_games,
    get_need_dispatch_players,
)
from etl_service.core.transformer import (
    get_update_url,
    transform_match_detail_data,
    transform_match_list_data,
    transform_profile_data,
)
from shared.models import EPOCH_START_TIME, Game, GameModel, Player


def get_default_last_match_time():
    return datetime.utcnow() - timedelta(days=3)


async def sync_games(engine: AsyncEngine, games: list[Game]):
    async with ClientSession() as session:
        coros = [
            get_match_detail_data(
                session, game.region, game.origin_player_name, game.id
            )
            for game in games
        ]
        game_datas = await asyncio.gather(*coros)
    logger.info("Done Extract Data")
    game_mdls: list[GameModel] = []
    for game, game_data in zip(games, game_datas):
        game_players = transform_match_detail_data(game_data)
        game_mdl = GameModel(game=game, players=game_players)
        game_mdls.append(game_mdl)
    logger.info("Done Transform Data")
    for game_mdl in game_mdls:
        logger.info(f"Load game {game_mdl.game.id}")
        async with engine.begin() as conn:
            await load_game_detail(conn, game_mdl)
    logger.info("Done Load Data")
    logger.success("Done sync games")


async def get_and_sync_games(engine: AsyncEngine, batch_size=10):
    logger.info("Start sync games")
    games = await get_need_dispatch_games(batch_size)
    logger.info(f"Get {len(games)} games")
    await sync_games(engine, games)


async def get_latest_profile_data(player: Player, session) -> str | None:
    try:
        profile_data = await get_profile_data(
            session, player.region, player.player_name
        )
        update_url = get_update_url(profile_data, player.player_name)
        await update_profile_data(session, update_url)
        profile_data = await get_profile_data(
            session, player.region, player.player_name
        )
        return profile_data
    except Exception as e:
        logger.error(f"Error when get profile data: {e}")
        return None


async def sync_player(engine: AsyncEngine, player: Player):
    async with ClientSession() as session:
        profile_data = await get_latest_profile_data(player, session)
    if not profile_data:
        logger.error(f"Sync player {player.player_name} failed")
        return
    updated_player = transform_profile_data(profile_data, player.player_name)
    logger.info("Done Get Profile")
    game_list, updated_last_match_time = await get_player_games(player)
    logger.info("Done Get Game List")
    async with engine.begin() as conn:
        await load_player(conn, updated_player)
        for game in game_list:
            await load_game(conn, game)
        player.last_match_time = updated_last_match_time
        await conn.execute(
            update(Player)
            .where(Player.id == player.id)
            .values(
                last_match_time=updated_last_match_time,
                last_sync_time=datetime.now(),
                next_sync_time=datetime.utcnow() + timedelta(days=1),
            )
        )
    logger.info("Done Load Data")
    logger.success(f"Done sync player {player.player_name}")


async def get_player_games(player: Player):
    async with ClientSession() as session:
        page = 1
        match_list = []
        if player.last_match_time == EPOCH_START_TIME:
            player.last_match_time = get_default_last_match_time()
        updated_last_match_time = player.last_match_time
        while True:
            match_list_data = await get_match_data(
                session, player.region, player.player_name, page=page
            )
            page_match_list = transform_match_list_data(match_list_data, player)
            if not page_match_list:
                logger.warning(f"No more matches for {player.player_name}, {page=}")
                break
            match_list.extend(page_match_list)
            match_start_times = [match.game_start_time for match in page_match_list]
            min_match_start_time = min(match_start_times)
            max_match_start_time = max(match_start_times)
            updated_last_match_time = max(updated_last_match_time, max_match_start_time)
            if min_match_start_time < player.last_match_time:
                break
            page += 1
    return match_list, updated_last_match_time


async def sync_players(engine: AsyncEngine, players: list[Player]):
    coros = [sync_player(engine, player) for player in players]
    await asyncio.gather(*coros)
    logger.success("Done sync players")


async def get_and_sync_players(engine: AsyncEngine, batch_size=10):
    logger.info("Start sync players")
    players = await get_need_dispatch_players(batch_size)
    logger.info(f"Get {len(players)} players")
    await sync_players(engine, players)
